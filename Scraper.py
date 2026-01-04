import requests
import pandas as pd
from datetime import datetime
from ics import Calendar, Event

# ---------------------------------------------------------
# Scrape Nasdaq ex-dividend data
# ---------------------------------------------------------
def scrape_nasdaq():
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Origin": "https://www.nasdaq.com",
        "Referer": "https://www.nasdaq.com/"
    }

    all_rows = []

    # Pull the next 7 days of data
    for i in range(7):
        date = (datetime.today() + pd.Timedelta(days=i)).strftime("%Y-%m-%d")
        url = f"https://api.nasdaq.com/api/calendar/dividends?date={date}"

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        data = response.json()

        rows = data["data"]["calendar"]["rows"]
        if rows:
            all_rows.extend(rows)

    df = pd.DataFrame(all_rows)
    print("Columns found:", df.columns.tolist())
    print(df.head())

    return df


# ---------------------------------------------------------
# Clean and normalize data
# ---------------------------------------------------------
def clean_dataframe(df):
    # Convert Nasdaq's ex-dividend date field
    df["dividend_Ex_Date"] = pd.to_datetime(df["dividend_Ex_Date"], errors="coerce")

    # Drop rows with invalid dates
    df = df.dropna(subset=["dividend_Ex_Date"])

    return df


# ---------------------------------------------------------
# Generate ICS calendar
# ---------------------------------------------------------
def generate_ics(df, output_file="exdiv.ics"):
    calendar = Calendar()

    for _, row in df.iterrows():
        event = Event()
        ticker = row["symbol"]
        company = row["companyName"]
        ex_date = row["dividend_Ex_Date"]


        event.name = f"{ticker} Ex-Dividend Date"
        event.begin = ex_date.strftime("%Y-%m-%d")
        event.make_all_day()

        event.description = (
            f"Company: {company}\n"
            f"Ticker: {ticker}\n"
            f"Dividend: {row.get('amount', '')}\n"
            f"Pay Date: {row.get('paymentDate', '')}"
        )

        calendar.events.add(event)

    with open(output_file, "w", encoding="utf-8") as f:
        f.writelines(calendar)

    print(f"ICS file written to {output_file}")

# ---------------------------------------------------------
# Main execution
# ---------------------------------------------------------
def main():
    print("Scraping Nasdaq ex-dividend data...")
    df = scrape_nasdaq()

    print("Cleaning data...")
    df = clean_dataframe(df)

    print("Generating ICS calendar...")
    generate_ics(df)

    print("Done.")

if __name__ == "__main__":
    main()
