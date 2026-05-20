import os
import sys

from groq import Groq

# Initialize the client with API key from environment variable
client = Groq(api_key=os.environ["GROQ_API_KEY"])


# Define a function that takes a code diff as input
def review_code(diff_text):
    prompt = f"""You are an expert code reviewer. Review the following code diff and provide feedback.

Focus on:
1. Security vulnerabilities
2. Bug risks
3. Performance issues
4. Best practice violations

For each issue you find, use this format:
- Severity: HIGH, MEDIUM, or LOW
- Description: brief explanation of the issue
- Suggested fix: clear recommendation to fix it

If the code looks good, say so.

End with exactly one line in this format:
SEVERITY_SUMMARY: <level>

Rules for <level>:
- CRITICAL = if any issue is HIGH severity
- WARNING = if issues are only MEDIUM or LOW severity
- GOOD = if no issues are found

Code diff to review:

{diff_text}

Provide your review in a clear, structured format, ending with the SEVERITY_SUMMARY line."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


def parse_severity(review_text):
    """Extract severity level from the review output."""
    for line in review_text.strip().split("\n"):
        if line.strip().startswith("SEVERITY_SUMMARY:"):
            level = line.split(":", 1)[1].strip().upper()
            if level in ("CRITICAL", "WARNING", "GOOD"):
                return level
    return "WARNING"  # Default to WARNING if parsing fails


# Only run this code when the script is executed directly
if __name__ == "__main__":
    # Check if a filename was passed as a command-line argument
    if len(sys.argv) > 1:
        # Get the filename from sys.argv and read the file
        diff_file = sys.argv[1]
        with open(diff_file, "r") as f:
            diff_content = f.read()
    else:
        # If no filename was passed, read from standard input
        diff_content = sys.stdin.read()

    # Call the review function and print the result
    review = review_code(diff_content)
    severity = parse_severity(review)
    print(review)

    with open("severity.txt", "w") as f:
        f.write(severity)
