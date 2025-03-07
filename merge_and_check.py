import pandas as pd
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def merge_and_check_data():
    try:
        # Read both CSV files
        df1 = pd.read_csv('olx_bikes_20250307_122843.csv')
        df2 = pd.read_csv('olx_bikes_20250307_131244.csv')
        
        # Basic info about each file
        logger.info(f"First file (early pages) shape: {df1.shape}")
        logger.info(f"Second file (later pages) shape: {df2.shape}")
        
        # Check page numbers in each file
        pages1 = df1['page_number'].unique()
        pages2 = df2['page_number'].unique()
        logger.info(f"Pages in first file: {sorted(pages1)}")
        logger.info(f"Pages in second file: {sorted(pages2)}")
        
        # Check for overlap in page numbers
        overlap = set(pages1).intersection(set(pages2))
        if overlap:
            logger.warning(f"Overlapping pages found: {sorted(overlap)}")
            # Remove overlapping pages from df1 (keep them in df2)
            df1 = df1[~df1['page_number'].isin(overlap)]
            logger.info(f"After removing overlap, first file shape: {df1.shape}")
        
        # Merge the dataframes
        df_merged = pd.concat([df1, df2], ignore_index=True)
        
        # Remove any duplicates (just in case)
        df_merged = df_merged.drop_duplicates()
        
        # Sort by page number
        df_merged = df_merged.sort_values(['page_number'])
        
        # Data quality checks
        logger.info("\nData Quality Checks:")
        logger.info(f"Total number of listings: {len(df_merged)}")
        logger.info(f"Number of unique pages: {df_merged['page_number'].nunique()}")
        logger.info(f"Average listings per page: {len(df_merged) / df_merged['page_number'].nunique():.2f}")
        
        # Check listings per page
        listings_per_page = df_merged.groupby('page_number').size()
        logger.info("\nListings per page analysis:")
        logger.info(f"Pages with less than 40 listings: {listings_per_page[listings_per_page < 40]}")
        logger.info(f"Pages with more than 40 listings: {listings_per_page[listings_per_page > 40]}")
        
        # Price analysis
        logger.info("\nPrice Analysis:")
        logger.info(f"Average price: ₹{df_merged['price'].mean():,.2f}")
        logger.info(f"Median price: ₹{df_merged['price'].median():,.2f}")
        logger.info(f"Price range: ₹{df_merged['price'].min():,} to ₹{df_merged['price'].max():,}")
        
        # Year analysis
        df_merged['year'] = pd.to_numeric(df_merged['year'], errors='coerce')
        logger.info("\nYear Analysis:")
        logger.info(f"Year range: {df_merged['year'].min()} to {df_merged['year'].max()}")
        
        # Save merged file
        output_file = 'olx_bikes_merged.csv'
        df_merged.to_csv(output_file, index=False)
        logger.info(f"\nMerged data saved to: {output_file}")
        
        return df_merged
        
    except Exception as e:
        logger.error(f"Error during merge and check: {str(e)}")
        raise

if __name__ == "__main__":
    merge_and_check_data() 