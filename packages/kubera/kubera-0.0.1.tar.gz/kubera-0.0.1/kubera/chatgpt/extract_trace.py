#!/usr/bin/env python3
"""
Extract ChatGPT conversation data into trace format.

Extracts the following fields for each message:
- session_uuid: conversation_id from top level
- message_uuid: message id
- parent_uuid: parent id from the mapping structure
- role: user/assistant/system from message author
- timestamp: create_time from message
- tokens: calculated from content parts (text only, skipping images/audio)
"""

import argparse
import csv
import datetime
import json
import os

from transformers import AutoTokenizer


def get_tokenizer(model_name="deepseek-ai/DeepSeek-V3"):
    """Load and return the specified tokenizer."""
    return AutoTokenizer.from_pretrained(model_name)


def count_text_tokens(text, tokenizer):
    """Count tokens using the specified tokenizer."""
    if not text:
        return 0

    tokens = tokenizer.encode(text, add_special_tokens=False)
    return len(tokens)


def extract_message_tokens(message, tokenizer):
    """Extract token count from message content parts."""
    if not message or "content" not in message:
        return 0

    content = message["content"]
    if not content:
        return 0

    total_tokens = 0

    # Handle content_type: text
    if (
        content.get("content_type") == "text"
        or content.get("content_type") == "execution_output"
        or content.get("content_type") == "system_error"
    ):
        parts = content.get("parts", [])
        for part in parts:
            if isinstance(part, str):
                total_tokens += count_text_tokens(part, tokenizer)
    elif content.get("content_type") == "tether_browsing_display":
        total_tokens += count_text_tokens(content.get("summary", ""), tokenizer)
    elif content.get("content_type") == "tether_quote":
        total_tokens += count_text_tokens(content.get("text", ""), tokenizer)
    elif content.get("content_type") == "thoughts":
        parts = content.get("thoughts", [])
        for part in parts:
            if isinstance(part["content"], str):
                total_tokens += count_text_tokens(part["content"], tokenizer)
    elif content.get("content_type") == "code":
        total_tokens += count_text_tokens(content["text"], tokenizer)

    # Extract tool metadata
    metadata = content.get("metadata", {})
    if not metadata:
        return total_tokens

    if metadata.get("search_result_groups"):
        for search_result_group in metadata["search_result_groups"]:
            entries = search_result_group.get("entry")
            for entry in entries:
                if entry.get("type") == "search_result":
                    total_tokens += count_text_tokens(
                        entry["url"] + entry["title"] + entry["snippet"], tokenizer
                    )
    elif metadata.get("search_queries"):
        for search_query in metadata["search_queries"]:
            total_tokens += count_text_tokens(search_query["q"], tokenizer)

    return total_tokens


def extract_conversation_trace(conversation_data, tokenizer):
    """Extract trace data from a single conversation."""
    results = []

    conversation_id = conversation_data.get("conversation_id")
    mapping = conversation_data.get("mapping", {})

    for node_id, node_data in mapping.items():
        message = node_data.get("message")

        # Skip nodes without messages
        if not message:
            continue

        # Skip system messages that are visually hidden
        metadata = message.get("metadata", {})

        if (
            metadata.get("is_visually_hidden_from_conversation")
            or not message.get("create_time")
            or not message.get("author")
        ):
            continue

        author = message.get("author")
        role = author.get("role")

        # Convert timestamp (epoch seconds to ISO format if needed)
        create_time = message.get("create_time")

        dt = datetime.datetime.fromtimestamp(create_time, tz=datetime.timezone.utc)
        timestamp = dt.isoformat()

        # Count tokens from content
        tokens = extract_message_tokens(message, tokenizer)

        # Get parent UUID
        parent_uuid = node_data.get("parent")

        row = {
            "session_uuid": conversation_id,
            "message_uuid": message.get("id"),
            "parent_uuid": parent_uuid,
            "role": role,
            "timestamp": timestamp,
            "tokens": tokens,
        }

        results.append(row)

    return results


def main():
    """Main function to process ChatGPT conversations and create CSV output."""
    parser = argparse.ArgumentParser(
        description="Extract ChatGPT conversation trace data."
    )
    parser.add_argument(
        "--input-file", type=str, required=True, help="Path to conversations.json file."
    )
    parser.add_argument(
        "--output-file",
        type=str,
        default="./data/chatgpt_trace.csv",
        help="Output CSV file name.",
    )
    parser.add_argument(
        "--tokenizer",
        type=str,
        default="deepseek-ai/DeepSeek-V3",
        help="Tokenizer model name.",
    )
    args = parser.parse_args()

    if not os.path.exists(args.input_file):
        print(f"Input file not found: {args.input_file}")
        return

    print(f"Processing ChatGPT conversations from: {args.input_file}")

    # Load tokenizer
    print(f"Loading tokenizer: {args.tokenizer}")
    tokenizer = get_tokenizer(args.tokenizer)

    # Load conversations data
    try:
        with open(args.input_file, "r", encoding="utf-8") as f:
            conversations_data = json.load(f)
    except Exception as e:
        print(f"Error reading input file: {e}")
        return

    # Ensure conversations_data is a list
    if not isinstance(conversations_data, list):
        print("Expected conversations data to be a list")
        return

    # Collect all trace data
    all_results = []
    print(f"Processing {len(conversations_data)} conversations...")

    for i, conversation in enumerate(conversations_data):
        if i % 100 == 0:
            print(f"Processed {i} conversations...")

        try:
            results = extract_conversation_trace(conversation, tokenizer)
            all_results.extend(results)
        except Exception as e:
            print(f"Error processing conversation {i}: {e}")
            continue

    # Create output directory if needed
    output_dir = os.path.dirname(args.output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if not all_results:
        print("\nNo trace data extracted.")
        return

    # Define CSV headers
    headers = [
        "session_uuid",
        "message_uuid",
        "parent_uuid",
        "role",
        "timestamp",
        "tokens",
    ]

    # Write CSV file
    if os.path.exists(args.output_file):
        with open(args.output_file, "a", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writerows(all_results)
    else:
        with open(args.output_file, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(all_results)

    print(
        f"\nSuccessfully extracted {len(all_results)} trace entries to {args.output_file}"
    )


if __name__ == "__main__":
    main()
