#!/usr/bin/env python3
"""
Extract Claude usage data from ~/.claude/projects JSONL files into CSV format.

Extracts the following fields:
- timestamp
- parentUuid
- sessionId
- uuid
- input_tokens (original input_tokens from usage data)
- cache_creation_input_tokens
- cache_read_input_tokens
- output_tokens
- total_input_tokens (calculated as: input_tokens + cache_creation_input_tokens + cache_read_input_tokens)
"""

import argparse
import csv
import glob
import json
import os


def extract_usage_data(jsonl_file):
    """Extract usage data from a single JSONL file."""
    results = []

    try:
        with open(jsonl_file, "r") as f:
            for line in f:
                try:
                    data = json.loads(line.strip())

                    # Check if this entry has usage data
                    if data.get("type") == "assistant" and "message" in data:
                        message = data.get("message", {})
                        usage = message.get("usage", {})

                        if not usage:
                            continue

                        # Extract required fields
                        row = {
                            "timestamp": data.get("timestamp", ""),
                            "parentUuid": data.get("parentUuid", ""),
                            "sessionId": data.get("sessionId", ""),
                            "uuid": data.get("uuid", ""),
                            "input_tokens": usage.get("input_tokens", 0),
                            "cache_creation_input_tokens": usage.get(
                                "cache_creation_input_tokens", 0
                            ),
                            "cache_read_input_tokens": usage.get(
                                "cache_read_input_tokens", 0
                            ),
                            "output_tokens": usage.get("output_tokens", 0),
                        }

                        # Calculate total input_tokens
                        row["total_input_tokens"] = (
                            row["input_tokens"]
                            + row["cache_creation_input_tokens"]
                            + row["cache_read_input_tokens"]
                        )

                        results.append(row)

                except json.JSONDecodeError:
                    continue
                except Exception as e:
                    print(f"Error processing line in {jsonl_file}: {e}")
                    continue

    except Exception as e:
        print(f"Error reading file {jsonl_file}: {e}")

    return results


def main():
    """Main function to process all JSONL files and create CSV output."""
    parser = argparse.ArgumentParser(
        description="Extract Claude usage data from JSONL files."
    )
    parser.add_argument(
        "--claude-dir",
        type=str,
        default="~/.claude",
        help="Directory containing Claude JSONL files.",
    )
    parser.add_argument(
        "--output-file",
        type=str,
        default="./data/claude_code_trace.csv",
        help="Output CSV file name.",
    )
    args = parser.parse_args()

    # Get all JSONL files from ~/.claude/projects
    claude_dir = os.path.expanduser(args.claude_dir)

    if not os.path.exists(claude_dir):
        print(f"Directory not found: {claude_dir}")
        return

    # Find all JSONL files recursively
    jsonl_files = glob.glob(os.path.join(claude_dir, "**/*.jsonl"), recursive=True)

    if not jsonl_files:
        print(f"No JSONL files found in {claude_dir}")
        return

    print(f"Found {len(jsonl_files)} JSONL files to process...")

    # Collect all usage data
    all_results = []
    for jsonl_file in jsonl_files:
        print(f"Processing: {jsonl_file}")
        results = extract_usage_data(jsonl_file)
        all_results.extend(results)

    # Write to CSV
    # make sure the output directory exists
    output_dir = os.path.dirname(args.output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_file = args.output_file

    if not all_results:
        print("\nNo usage data found in any JSONL files.")
        return

    # Define CSV headers
    headers = [
        "timestamp",
        "parentUuid",
        "sessionId",
        "uuid",
        "input_tokens",
        "cache_creation_input_tokens",
        "cache_read_input_tokens",
        "output_tokens",
        "total_input_tokens",
    ]

    # Write CSV file
    # If file already exists, append to it
    if os.path.exists(output_file):
        with open(output_file, "a", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writerows(all_results)
    else:
        with open(output_file, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(all_results)

    print(f"\nSuccessfully extracted {len(all_results)} usage entries to {output_file}")


if __name__ == "__main__":
    main()
