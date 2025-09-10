#!/usr/bin/env python3
"""
Extract Claude web conversation data into trace format.

Extracts the following fields for each message:
- session_uuid: conversation uuid from top level
- message_uuid: message uuid
- parent_uuid: not available in Claude web format, will be empty
- role: sender (human/assistant)
- start_timestamp: start_timestamp from content or created_at
- stop_timestamp: stop_timestamp from content or created_at
- tokens: calculated from content parts (text only, skipping images/audio)
"""

import argparse
import csv
import json
import os
import uuid

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
    total_tokens = 0

    if message.get("type") == "text":
        part_text = message.get("text", "")
        total_tokens += count_text_tokens(part_text, tokenizer)
    if message.get("type") == "tool_use" and message.get("name") == "artifacts":
        tool_input = message.get("input", {})
        if tool_input:
            if tool_input.get("command") == "update":
                new_str = tool_input.get("new_str", "")
                old_str = tool_input.get("old_str", "")
                total_tokens += count_text_tokens(new_str, tokenizer)
                total_tokens += count_text_tokens(old_str, tokenizer)
            elif (
                tool_input.get("command") == "create"
                or tool_input.get("command") == "rewrite"
            ):
                content = tool_input.get("content", "")
                total_tokens += count_text_tokens(content, tokenizer)
    elif (
        message.get("type") == "tool_use"
        and message.get("name") == "launch_extended_search_task"
    ):
        tool_input = message.get("input", {})
        if tool_input:
            query = tool_input.get("command", "")
            total_tokens += count_text_tokens(query, tokenizer)
    elif message.get("type") == "tool_use" and message.get("name") == "repl":
        tool_input = message.get("input", {})
        if tool_input:
            query = tool_input.get("code", "")
            total_tokens += count_text_tokens(query, tokenizer)
    elif message.get("type") == "tool_use" and message.get("name") == "web_search":
        tool_input = message.get("input", {})
        if tool_input:
            query = tool_input.get("query", "")
            total_tokens += count_text_tokens(query, tokenizer)
    elif message.get("type") == "tool_result":
        _content_parts = message.get("content_parts", [])
        for _part in _content_parts:
            if _part.get("type") == "text":
                _part_text = _part.get("text", "")
                total_tokens += count_text_tokens(_part_text, tokenizer)

    return total_tokens


def extract_conversation_trace(conversation_data, tokenizer):
    """Extract trace data from a single Claude web conversation."""
    results = []

    conversation_uuid = conversation_data.get("uuid", "")
    if not conversation_uuid:
        # Generate a UUID if not present
        conversation_uuid = str(uuid.uuid4())

    chat_messages = conversation_data.get("chat_messages", [])

    for message in chat_messages:
        message_uuid = message.get("uuid", "")
        if not message_uuid:
            message_uuid = str(uuid.uuid4())

        # Get role from sender field
        role = message.get("sender", "unknown")

        # Get timestamps - check content first, then fallback to created_at
        start_timestamp = ""
        stop_timestamp = ""

        # Check content parts for timestamps
        content_parts = message.get("content", [])
        if content_parts:
            # Use first content part's timestamps
            first_content = content_parts[0]
            start_timestamp = first_content.get("start_timestamp", "")
            stop_timestamp = first_content.get("stop_timestamp", "")

        # Fallback to created_at if no timestamps in content
        if not start_timestamp:
            start_timestamp = message.get("created_at", "")
            stop_timestamp = start_timestamp

        for i, content in enumerate(content_parts):
            if role == "assistant" and content.get("type") == "tool_result":
                _role = "tool"
            else:
                _role = role

            tokens = extract_message_tokens(content, tokenizer)

            if role == "human":
                attachments = message.get("attachments", [])
                if attachments:
                    for part in attachments:
                        if part.get("extracted_content"):
                            part_text = part.get("extracted_content", "")
                            tokens += count_text_tokens(part_text, tokenizer)

            row = {
                "session_uuid": conversation_uuid,
                "message_uuid": message_uuid + "_" + str(i),
                "role": _role,
                "start_timestamp": start_timestamp,
                "stop_timestamp": stop_timestamp,
                "tokens": tokens,
            }

            results.append(row)

    return results


def main():
    """Main function to process Claude web conversations and create CSV output."""
    parser = argparse.ArgumentParser(
        description="Extract Claude web conversation trace data."
    )
    parser.add_argument(
        "--input-file", type=str, required=True, help="Path to conversations.json file."
    )
    parser.add_argument(
        "--output-file",
        type=str,
        default="./data/claude_web_trace.csv",
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

    print(f"Processing Claude web conversations from: {args.input_file}")

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
        "role",
        "start_timestamp",
        "stop_timestamp",
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
