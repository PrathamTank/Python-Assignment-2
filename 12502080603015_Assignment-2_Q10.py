import os
import pandas as pd
import matplotlib.pyplot as plt

print("=== Python Data Visualization Dashboard Exporter ===")

file_path = input("Enter marks CSV file path: ").strip()
output_folder = input("Enter output folder path: ").strip()

try:
    os.makedirs(output_folder, exist_ok=True)

    df = pd.read_csv(file_path)

    if "enrollment" not in df.columns or "name" not in df.columns:
        raise ValueError("CSV must contain enrollment and name columns.")

    subject_columns = [
        column for column in df.columns
        if column not in ("enrollment", "name")
    ]

    if not subject_columns:
        raise ValueError("No subject columns found.")

    df[subject_columns] = df[subject_columns].apply(
        pd.to_numeric, errors="coerce"
    )

    for subject in subject_columns:
        df.loc[~df[subject].between(0, 100), subject] = float("nan")
        df[subject] = df[subject].fillna(df[subject].mean())

    df[subject_columns] = df[subject_columns].fillna(0)

    cleaned_path = os.path.join(output_folder, "cleaned_marks.csv")
    df.to_csv(cleaned_path, index=False)

    summary = pd.DataFrame({
        "Subject": subject_columns,
        "Average": [df[s].mean() for s in subject_columns],
        "Minimum": [df[s].min() for s in subject_columns],
        "Maximum": [df[s].max() for s in subject_columns],
        "Standard Deviation": [df[s].std() for s in subject_columns]
    })

    summary_path = os.path.join(output_folder, "summary.csv")
    summary.to_csv(summary_path, index=False)

    average_marks = df[subject_columns].mean(axis=1)

    def get_grade(mark):
        if mark >= 90:
            return "A"
        elif mark >= 80:
            return "B"
        elif mark >= 70:
            return "C"
        elif mark >= 60:
            return "D"
        else:
            return "F"

    grades = average_marks.apply(get_grade)
    grade_counts = grades.value_counts().reindex(
        ["A", "B", "C", "D", "F"], fill_value=0
    )

    plt.figure(figsize=(7, 5))
    grade_counts.plot(kind="bar")
    plt.title("Grade Distribution")
    plt.xlabel("Grade")
    plt.ylabel("Number of Students")
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, "grade_distribution.png"))
    plt.close()

    plt.figure(figsize=(8, 5))
    summary.set_index("Subject")["Average"].plot(kind="bar")
    plt.title("Subject-wise Average Marks")
    plt.xlabel("Subject")
    plt.ylabel("Average Marks")
    plt.ylim(0, 100)
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, "subject_average.png"))
    plt.close()

    top_students = df.copy()
    top_students["Average"] = average_marks
    top_students = top_students.nlargest(10, "Average")
    top_students = top_students.sort_values("Average")

    plt.figure(figsize=(9, 6))
    plt.barh(
        top_students["name"].astype(str),
        top_students["Average"]
    )
    plt.title("Top 10 Student Performers")
    plt.xlabel("Average Marks")
    plt.ylabel("Student Name")
    plt.xlim(0, 100)
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, "top_performers.png"))
    plt.close()

    print("\nProcessing completed successfully.")
    print("Cleaned CSV:", cleaned_path)
    print("Summary CSV:", summary_path)
    print("Chart:", os.path.join(output_folder, "grade_distribution.png"))
    print("Chart:", os.path.join(output_folder, "subject_average.png"))
    print("Chart:", os.path.join(output_folder, "top_performers.png"))

except (OSError, ValueError, pd.errors.ParserError) as e:
    print("ERROR:", e)