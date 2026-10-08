"""
Problem 2: API Data Processing and Visualization
------------------------------------------------
Fetches student test-score data from the local mock REST API (http://127.0.0.1:8000/students),
validates scores, filters invalid/missing entries, computes the class average formatted to
two decimal places, and generates a clean Matplotlib bar chart.

Author: Vimlesh Tiwari
"""

import sys
from typing import Any, Dict, List, Optional, Tuple
import matplotlib
matplotlib.use("Agg")  # Standard non-interactive backend for server/CLI environments
import matplotlib.pyplot as plt
import requests

API_URL = "http://127.0.0.1:8000/students"
CHART_OUTPUT_FILE = "student_scores_chart.png"


def fetch_student_data(url: str = API_URL, timeout: int = 5) -> List[Dict[str, Any]]:
    """
    Fetch student test score records from the REST API.
    
    Args:
        url: The API endpoint URL.
        timeout: Request timeout in seconds.
        
    Returns:
        List of raw student dictionaries.
    """
    print(f"[*] Fetching student test-score data from: {url}")
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.ConnectionError:
        print("[ERROR] Could not connect to the mock API server.", file=sys.stderr)
        print("[TIP] Ensure 'python mock_student_api.py' is running in another terminal.", file=sys.stderr)
        return []
    except requests.exceptions.Timeout:
        print("[ERROR] Request to student API timed out.", file=sys.stderr)
        return []
    except requests.exceptions.HTTPError as http_err:
        print(f"[ERROR] HTTP error returned by API: {http_err}", file=sys.stderr)
        return []
    except requests.exceptions.RequestException as req_err:
        print(f"[ERROR] An error occurred during request: {req_err}", file=sys.stderr)
        return []
    except ValueError as json_err:
        print(f"[ERROR] Failed to parse API JSON response: {json_err}", file=sys.stderr)
        return []

    if not isinstance(data, list):
        print("[ERROR] Expected a JSON list of student records.", file=sys.stderr)
        return []

    if not data:
        print("[WARNING] API returned an empty student dataset.")
        return []

    print(f"[SUCCESS] Successfully fetched {len(data)} record(s) from API.")
    return data


def process_student_scores(data: List[Dict[str, Any]]) -> Tuple[List[str], List[float]]:
    """
    Validate and extract student names and numeric test scores.
    Ignores records with missing, null, or invalid scores.
    
    Args:
        data: Raw student records from API.
        
    Returns:
        Tuple containing list of valid student names and list of numeric scores.
    """
    names: List[str] = []
    scores: List[float] = []

    if not data:
        return names, scores

    for index, item in enumerate(data, start=1):
        if not isinstance(item, dict):
            print(f"[WARNING] Skipping item {index}: Record is not a valid dictionary.")
            continue

        raw_name = item.get("name")
        raw_score = item.get("score")

        # Validate name
        if not raw_name or not str(raw_name).strip():
            print(f"[WARNING] Skipping item {index}: Missing student name.")
            continue
        clean_name = str(raw_name).strip()

        # Validate score
        if raw_score is None:
            print(f"[WARNING] Skipping '{clean_name}': Score is missing/None.")
            continue

        try:
            numeric_score = float(raw_score)
            if numeric_score < 0:
                print(f"[WARNING] Skipping '{clean_name}': Negative score {numeric_score} is invalid.")
                continue
            names.append(clean_name)
            scores.append(numeric_score)
        except (ValueError, TypeError):
            print(f"[WARNING] Skipping '{clean_name}': Invalid non-numeric score '{raw_score}'.")

    return names, scores


def calculate_average_score(scores: List[float]) -> Optional[float]:
    """
    Calculate the arithmetic mean of student test scores.
    """
    if not scores:
        return None
    return sum(scores) / len(scores)


def plot_student_scores(
    names: List[str],
    scores: List[float],
    avg_score: Optional[float],
    output_path: str = CHART_OUTPUT_FILE
) -> None:
    """
    Generate a bar chart using Matplotlib and save to disk.
    
    - X-axis: Student Names
    - Y-axis: Test Scores
    - Title: Student Test Scores
    """
    if not names or not scores:
        print("[!] Cannot generate visualization: No valid data available.")
        return

    plt.figure(figsize=(8, 5.5))
    
    # Clean bar styling
    colors = ["#3B82F6", "#06B6D4", "#10B981", "#F59E0B", "#EF4444"]
    bar_colors = [colors[i % len(colors)] for i in range(len(names))]
    bars = plt.bar(names, scores, color=bar_colors, width=0.5, edgecolor="#1E293B", linewidth=1.2, zorder=3)

    # Plot average reference line if available
    if avg_score is not None:
        plt.axhline(
            y=avg_score,
            color="#DC2626",
            linestyle="--",
            linewidth=1.8,
            label=f"Average Score ({avg_score:.2f})",
            zorder=4
        )

    # Annotate score values on top of each bar
    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2.0,
            height + 1.2,
            f"{height:.1f}",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold"
        )

    plt.title("Student Test Scores", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Student Names", fontsize=11, fontweight="bold", labelpad=10)
    plt.ylabel("Test Scores", fontsize=11, fontweight="bold", labelpad=10)
    plt.ylim(0, max(max(scores) + 15, 100))
    plt.grid(axis="y", linestyle=":", alpha=0.6, zorder=0)
    plt.legend(loc="upper right", frameon=True)
    plt.tight_layout()

    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"[SUCCESS] Matplotlib chart saved successfully as '{output_path}'.")


def main() -> None:
    """
    Main orchestration function for Problem 2.
    """
    print("\n--- Problem 2: API Data Processing & Visualization ---")

    # 1. Ingest data from API
    raw_data = fetch_student_data(API_URL)
    if not raw_data:
        print("[!] No data retrieved. Please ensure the mock API server is running.", file=sys.stderr)
        return

    # 2. Extract and validate student names and scores
    names, scores = process_student_scores(raw_data)
    if not names or not scores:
        print("[ERROR] No valid student score records available to process.", file=sys.stderr)
        return

    # 3. Print extracted records
    print("\n[+] Processed Student Scores:")
    for name, score in zip(names, scores):
        print(f"    - {name:<10}: {score:.2f}")

    # 4. Compute and display average score (formatted to 2 decimal places)
    average = calculate_average_score(scores)
    if average is not None:
        print("\n" + "=" * 32)
        print(f"Average Score: {average:.2f}")
        print("=" * 32 + "\n")

    # 5. Create Matplotlib visualization
    plot_student_scores(names, scores, average, CHART_OUTPUT_FILE)


if __name__ == "__main__":
    main()
