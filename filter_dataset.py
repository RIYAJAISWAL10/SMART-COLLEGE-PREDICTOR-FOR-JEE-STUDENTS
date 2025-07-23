import pandas as pd

# Load dataset
df = pd.read_csv('final_merged_dataset.csv')

# ✅ JEE ADVANCED DATASET (Only IITs, exclude IIITs)
jee_adv_df = df[df['Institute'].str.contains('Indian Institute of Technology', na=False) &
                ~df['Institute'].str.contains('Indian Institute of Information Technology', na=False)]

# ✅ JEE MAINS DATASET (NITs, IIITs, GFTIs, Others)
jee_main_df = df[df['Institute'].str.contains(
    'National Institute of Technology|Indian Institute of Information Technology|School|University|College', na=False)]

# Save outputs
jee_adv_df.to_csv('jee_advanced_data.csv', index=False)
jee_main_df.to_csv('jee_main_data.csv', index=False)

print("✅ Done: Filtered datasets saved successfully.")
