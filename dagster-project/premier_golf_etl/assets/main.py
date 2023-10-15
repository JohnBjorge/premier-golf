# import base64
# from io import BytesIO
# from typing import List

# import matplotlib.pyplot as plt
# import pandas as pd
# import requests
from dagster import AssetExecutionContext, MetadataValue, asset, get_dagster_logger
# from wordcloud import STOPWORDS, WordCloud

from premier_golf_etl.assets.premier_golf_scraper import PremierGolfScraper
from premier_golf_etl.assets.data_aggregator import DataAggregator
from datetime import date, timedelta
import concurrent.futures

logger = get_dagster_logger()

@asset(group_name="golf", compute_kind="scraper")
def threaded_scrape(context: AssetExecutionContext) -> None:
    start_date = date.today()
    number_of_days = 2

    dates_list = [start_date + timedelta(days=i) for i in range(number_of_days)]
    max_workers = 12

    logger.info(f"Scraping {number_of_days} days ({dates_list}) with maximum of {max_workers} workers.")
    # with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
    #     for day in dates_list:
    #         test = executor.submit(run_scraper, day)
    #         logger.info(f"test: {test}")


    results = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_day_scraper = {executor.submit(run_scraper, day): day for day in dates_list}
        
        for future in concurrent.futures.as_completed(future_day_scraper):
            day = future_day_scraper[future]
            day_formatted = day.strftime("%Y%m%d")
            try:
                result = future.result()  # This blocks until the future is complete
                results.append((day_formatted, result))
            except Exception as e:
                print(f"Error occurred for day {day_formatted}: {e}")
    
    context.add_output_metadata(
        metadata={
            "sample output": result,
            "total output": results
        }
    )

def run_scraper(date_search: date) -> None:
    pgs = PremierGolfScraper(date_search=date_search, course_search="Jackson Park")
    pgs.start_driver()
    html = pgs.navigate_page()
    tee_times = pgs.scrape(html)
    results = pgs.get_tee_time_search_results(tee_times)
    logger.info(f"Scraped {len(tee_times)} tee times for {date_search}")
    pgs.save_to_json(results)
    pgs.quit()
    return results


@asset(group_name="golf", compute_kind="aggregator", non_argument_deps={"threaded_scrape"})
def aggregate_data(context: AssetExecutionContext) -> DataAggregator:
    data_aggregator = DataAggregator()
    data_aggregator.aggregate_data()
    data_aggregator.save_data()
    context.add_output_metadata(
        {
            "filepath": data_aggregator.agg_file_path,
        }
    )
    return data_aggregator

@asset(group_name="golf", compute_kind="aggregator")
def upload_to_gcs(
        context: AssetExecutionContext, aggregate_data: DataAggregator
    ) -> None:
    aggregate_data.upload_to_google()

    context.add_output_metadata(
        {
            "filepath": aggregate_data.agg_file_path,
        }
    )


# PLAN todo
# Follow tutorial: https://docs.dagster.io/tutorial/building-an-asset-graph
# Add metadata so easier to see what's happening
# Schedule / create pipeline in init file
# Change to using io manager rather than writing files around
# Should make it easier to switch to using google cloud storage (toggle for local/production)

# Figure out pipeline step to take json files in GCS into raw table(s) in big query 
# Figure out how to deploy to compute engine (docker or devcontainer or manual deploy)
# Polish up process, code, etc, make it robust

# get setup with dbt to handle transformation steps of data
# incorporate dbt into pipeline
# When dbt transformations are good into prod table data model then figure out looker

# once accumulated lots of data consider ML stuff




# @asset(group_name="hackernews", compute_kind="HackerNews API")
# def hackernews_topstory_ids() -> List[int]:
#     """Get up to 500 top stories from the HackerNews topstories endpoint.

#     API Docs: https://github.com/HackerNews/API#new-top-and-best-stories
#     """
#     newstories_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
#     top_500_newstories = requests.get(newstories_url).json()
#     return top_500_newstories


# @asset(group_name="hackernews", compute_kind="HackerNews API")
# def hackernews_topstories(
#     context: AssetExecutionContext, hackernews_topstory_ids: List[int]
# ) -> pd.DataFrame:
#     """Get items based on story ids from the HackerNews items endpoint. It may take 1-2 minutes to fetch all 500 items.

#     API Docs: https://github.com/HackerNews/API#items
#     """
#     results = []
#     for item_id in hackernews_topstory_ids:
#         item = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json").json()
#         results.append(item)
#         if len(results) % 20 == 0:
#             context.log.info(f"Got {len(results)} items so far.")

#     df = pd.DataFrame(results)

#     # Dagster supports attaching arbitrary metadata to asset materializations. This metadata will be
#     # shown in the run logs and also be displayed on the "Activity" tab of the "Asset Details" page in the UI.
#     # This metadata would be useful for monitoring and maintaining the asset as you iterate.
#     # Read more about in asset metadata in https://docs.dagster.io/concepts/assets/software-defined-assets#recording-materialization-metadata
#     context.add_output_metadata(
#         {
#             "num_records": len(df),
#             "preview": MetadataValue.md(df.head().to_markdown()),
#         }
#     )
#     return df


# @asset(group_name="hackernews", compute_kind="Plot")
# def hackernews_topstories_word_cloud(
#     context: AssetExecutionContext, hackernews_topstories: pd.DataFrame
# ) -> bytes:
#     """Exploratory analysis: Generate a word cloud from the current top 500 HackerNews top stories.
#     Embed the plot into a Markdown metadata for quick view.

#     Read more about how to create word clouds in http://amueller.github.io/word_cloud/.
#     """
#     stopwords = set(STOPWORDS)
#     stopwords.update(["Ask", "Show", "HN"])
#     titles_text = " ".join([str(item) for item in hackernews_topstories["title"]])
#     titles_cloud = WordCloud(stopwords=stopwords, background_color="white").generate(titles_text)

#     # Generate the word cloud image
#     plt.figure(figsize=(8, 8), facecolor=None)
#     plt.imshow(titles_cloud, interpolation="bilinear")
#     plt.axis("off")
#     plt.tight_layout(pad=0)

#     # Save the image to a buffer and embed the image into Markdown content for quick view
#     buffer = BytesIO()
#     plt.savefig(buffer, format="png")
#     image_data = base64.b64encode(buffer.getvalue())
#     md_content = f"![img](data:image/png;base64,{image_data.decode()})"

#     # Attach the Markdown content as metadata to the asset
#     # Read about more metadata types in https://docs.dagster.io/_apidocs/ops#metadata-types
#     context.add_output_metadata({"plot": MetadataValue.md(md_content)})

#     return image_data
