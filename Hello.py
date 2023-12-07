import streamlit as st
import pandas as pd
from io import StringIO

def process_data(df, window_size):
    # Convert 'Price' to numeric, calculate moving average, and signal
    df['Price'] = pd.to_numeric(df['Price'].str.replace(',', ''), errors='coerce')
    df['Moving_Average'] = df['Price'].rolling(window=window_size).mean()
    df['Signal'] = df.apply(lambda row: 'Buy' if row['Price'] > row['Moving_Average'] else 'Sell', axis=1)
    
    # Add 'Decision' column
    df['Decision'] = df['Signal'].where(df['Signal'] != df['Signal'].shift(), 'Hold')
    
    # Filter data based on Decision
    df = df[df['Decision'].isin(['Buy', 'Sell']) & df['Moving_Average'].notnull()]
    
    # Add 'Diff' column
    df['Next_Price'] = df['Price'].shift(-1)
    df['Diff'] = df.apply(lambda row: row['Price'] - row['Next_Price'] if row['Decision'] == 'Buy' else row['Next_Price'] - row['Price'], axis=1)
    df = df.drop(columns=['Next_Price'])

    return df

def to_csv(df):
    output = StringIO()
    df.to_csv(output, index=False)
    return output.getvalue()

def display_statistics(df):
    st.write("Sum of Diff: ", df['Diff'].sum())
    st.write("Mean of Diff: ", df['Diff'].mean())
    st.write("Max of Diff: ", df['Diff'].max())
    st.write("Min of Diff: ", df['Diff'].min())

def main():
    st.title("Nifty 50 Data Processor")

    # Slider for selecting moving average window size
    window_size = st.slider('Select Moving Average Window Size', 5, 200, 50)

    # File uploader
    file = st.file_uploader("Upload your Nifty 50 Historical Data CSV", type=["csv"])
    if file is not None:
        data = pd.read_csv(file)
        processed_data = process_data(data, window_size)

        # Display statistics
        display_statistics(processed_data)

        # Download button
        if st.download_button(label="Download Processed Data as CSV",
                              data=to_csv(processed_data),
                              file_name='processed_nifty_50_data.csv',
                              mime='text/csv'):
            st.success('File has been downloaded!')

if __name__ == "__main__":
    main()
