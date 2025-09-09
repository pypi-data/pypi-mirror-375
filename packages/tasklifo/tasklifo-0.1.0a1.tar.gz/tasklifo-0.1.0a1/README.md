# tasklifo

![Logo](https://raw.githubusercontent.com/jifengwu2k/tasklifo/refs/heads/main/logo.svg)

> Last-in-first-out (LIFO), Git-inspired, LLM-assisted, Shell-friendly task manager for the busy and frequently interrupted.
> What does this logo mean? See [here](https://github.com/jifengwu2k/tasklifo?tab=readme-ov-file#explanation-of-logo) for an explanation.

## Why tasklifo?

Modern work is constant interruptions and context switches. 

- You juggle multiple projects and roles.
- Your day is **frequently interrupted** with meetings, interruptions, and "can you just..." requests.
- You have precious little time to sit down and carefully describe every new task - but you want your future self to have good context and actionable next steps.

Most task managers use FIFO - your latest, most urgent tasks get buried.  

tasklifo is a Shell tool designed for the real world, built on Unix principles *and* modern technology:

- **LIFO workflow:** Newest tasks are always on top - just like a stack.
- **Plain storage:** Everything is local, plain-text, and human-readable.
- **Composable:** Works with your shell, can be scripted, piped, or manipulated with standard Unix tools.
- **Git-like internals:** Attachments and blobs are hashed (SHA-1), tasks are JSON files - safe, deduplicated, portable.
- **LLM support:** Draft clear tasks with the help of language models, but you always review in your own `$EDITOR`.

## Features

- **LIFO workflow:** Latest tasks are always on top.
- **LLM-assisted task entry:** Draft task title/description with any LLM that implements the [OpenAI Chat Completions API](https://platform.openai.com/docs/api-reference/chat).
  - Including GPT, Gemini, DeepSeek, and local models (like Ollama) via compatible endpoints.
  - Review and edit LLM feedback with `$EDITOR`, just like editing a Git commit message.
- **Supports attachments:** Attach logs, screenshots, or any file to a task.
- **Git-like data storage:** Attachments stored content-addressed, tasks as plain JSON.
- **Works everywhere:** Python 2 & 3, POSIX & Windows, zero non-Python dependencies.

## Installation

```
pip install tasklifo
```

## Usage

> In the commands below, if `DIRECTORY` is omitted, defaults to a user-global `~/.tasklifo`.
> Providing `DIRECTORY` allows you to use different directories for different task LIFOs - for development, support, personal tasks, etc.

### Initialize an empty task LIFO in `DIRECTORY`

```
python -m tasklifo [--directory DIRECTORY] init 
```

### Push (add) a task, manually

```
python -m tasklifo [--directory DIRECTORY] push \
  [--title TITLE] \
  [--description DESCRIPTION] \
  [ATTACHMENT...]
```

- Copies attachments to `DIRECTORY/objects` Git-style.
- Creates a task JSON under `DIRECTORY/tasks/active` with ISO 8601 timestamp as file name, e.g., `DIRECTORY/tasks/active/20250908T000000Z.json`, storing:
    - Title
    - Description
    - SHA-1 hashes of attachments

### Push (add) a task, with LLM assistance

```
python -m tasklifo [--directory DIRECTORY] llmpush \
  --api-key API_KEY \
  --base-url BASE_URL \
  --model MODEL \
  [--message MESSAGE [--message MESSAGE]...] \
  [ATTACHMENT...]
```

- `API_KEY`, `BASE_URL`, `MODEL` follow OpenAI Chat Completions API conventions.
- One or more `--message` allows adding user messages (e.g., "I have to fix this error message") into the prompt sent to the LLM.
- If no `--message` is provided, ee launch the user's `$EDITOR`, just like editing a Git commit message.
- Attachments are supported as usual.
- LLM drafts task title and description.
- No LLM hallucination accepted blindly. We launch the user's `$EDITOR` and allow the user edit the LLM's output, just like editing a Git commit message.

### Get the top (most recent) task

```
python -m tasklifo [--directory DIRECTORY] top
```

- Dumps top task JSON to STDOUT.


### Log (list) all tasks

```
python -m tasklifo [--directory DIRECTORY] log [--all]
```

- Dumps task JSONs to STDOUT in reverse chronological order.
- By default, only dumps active tasks. Providing `--all` also dumps completed task JSONs.

### Checkout (retrieve) an attachment

```
python -m tasklifo [--directory DIRECTORY] checkout SHA1
```

- Dumps file contents to STDOUT.
- Use redirection (e.g., `> output.txt`) to write to a file.

### Pop (complete) a task

```
python -m tasklifo [--directory DIRECTORY] pop [TIMESTAMP]
```

- Defaults to popping the most recent task.
- Moves the task JSON from `DIRECTORY/tasks/active` to `DIRECTORY/tasks/completed`.
- Dumps the moved task JSON to STDOUT.

## Git-Style Local Storage

When you run `python -m tasklifo [--directory DIRECTORY] init`, it creates `DIRECTORY` with the following structure. Everything is *local*, *plain*. Fast, portable, no cloud, no lock-in, no database or server:

```yaml
- DIRECTORY
  # Content-addressable store for attachments
  # Like `.git/objects/`
  - objects/
    - ab/
      - c123def...
      - ...
  # Task JSONs, with ISO 8601 timestamps as file names
  - tasks/
    # Active tasks
    - active/
      - 20250908T000000Z.json
      - ...
    # Completed tasks
    - completed/
      - 20250907T000000Z.json
      - ...
```

## Example Task JSON

```json
{
    "timestamp": "20250908T000000Z",
    "title": "Send follow-up email",
    "description": "Email the customer with the debugging results.\nCheck attached log file.",
    "attachments": [
        {
            "sha1": "3f784781b4289ca5b5f7dc6789b4dcf6cd5e1d3b",
            "filename": "debug-log.txt"
        }
    ],
    "status": "active"
}
```

## Philosophy

- **Interrupt-driven workflow:** Treat new tasks as stack "pushes", pop each as done, and never lose momentum - even after being interrupted.
- **Context always captured:** Attach files, add detail, or use LLMs for well-formed entries without blank-page anxiety.
- **Human-in-the-loop:** LLM outputs are *never* saved without your review in an editor.
- **Unix philosophy, local control:**
  - *Do one thing well:* tasklifo just manages your LIFO task stack - no agenda, calendars, or proprietary ecosystem.
  - *Text streams and composition:* Input and output are simple. Pipe, redirect, and script as needed.
  -  *Local-first, human-readable:* No lock-in, no cloud, no silo. All your data is immediately accessible.
  -  *Git-inspired design:* Secure, deduplicated file storage; import into Git for versioning if you wish.

## Future Work: LLM-powered Semantic Search

### Why LLM-Powered Semantic Search?

- **Traditional search** is keyword-based. If you forgot an exact phrase or typo, you're out of luck.
- **Semantic search** (using LLM embeddings) lets you "find what you meant" - by intent, related concepts, even tone - across your tasks and attached content.
- **Burn out and memory issues:** If you only remember a fuzzy idea ("something about logs from last week" or "the meeting with the urgent customer bug"), you can still find it.

### Command Synopsis

```
python -m tasklifo [--directory DIRECTORY] llmgrep "all tasks where I attached a legal contract for review"
```

## Testing

- Make sure you have `coverage` installed.
- Set the `$API_KEY`, `$BASE_URL`, `$MODEL` environment variables.

### Quick Test

```bash
# Should either print "Initialized tasklifo in '/home/$USER/.tasklifo'"
# Or raise an exception if you have already initialized
python -m coverage run --append tasklifo.py init

# Should print a JSON resembling:
#{
#  "attachments": [], 
#  "description": "Task description", 
#  "timestamp": "...", 
#  "title": "My Task"
#}
python -m coverage run --append tasklifo.py push --title "My Task" --description "Task description"

# Should print a JSON resembling:
#{
#  "attachments": [], 
#  "description": "Task description", 
#  "timestamp": "...", 
#  "title": "My Task"
#}
python -m coverage run --append tasklifo.py top

# Should print a JSON resembling:
#{
#  "attachments": [], 
#  "description": "Second task description", 
#  "timestamp": "...", 
#  "title": "My Second Task"
#}
python -m coverage run --append tasklifo.py push --title "My Second Task" --description "Second task description"

# Should print a JSON resembling:
#{
#  "attachments": [], 
#  "description": "Second task description", 
#  "timestamp": "...", 
#  "title": "My Second Task"
#}
python -m coverage run --append tasklifo.py top

# Should print two JSONs resembling:
#{
#  "attachments": [], 
#  "description": "Second task description", 
#  "timestamp": "...", 
#  "title": "My Second Task"
#}
#{
#  "attachments": [], 
#  "description": "Task description", 
#  "timestamp": "...", 
#  "title": "My Task"
#}
python -m coverage run --append tasklifo.py log

# Should print a JSON resembling:
#{
#  "attachments": [], 
#  "description": "Second task description", 
#  "timestamp": "...", 
#  "title": "My Second Task"
#}
python -m coverage run --append tasklifo.py pop

# Should print a JSON resembling:
#{
#  "attachments": [], 
#  "description": "Task description", 
#  "timestamp": "...", 
#  "title": "My Task"
#}
python -m coverage run --append tasklifo.py log

# Should print two JSONs resembling:
#{
#  "attachments": [], 
#  "description": "Second task description", 
#  "timestamp": "...", 
#  "title": "My Second Task"
#}
#{
#  "attachments": [], 
#  "description": "Task description", 
#  "timestamp": "...", 
#  "title": "My Task"
#}
python -m coverage run --append tasklifo.py log --all

# Should start an interactive session
# Should print a JSON resembling:
#{
#  "attachments": [
#    {
#      "filename": "README.md", 
#      "sha1": "..."
#    }
#  ], 
#  "description": "Revise the tasklifo README to improve clarity, organization, and completeness. Ensure sections are clearly written, concise, and easy to follow. Check for grammar and style consistency, fill in any missing information, and enhance formatting where needed for better readability.", 
#  "timestamp": "...", 
#  "title": "Polish the tasklifo README for clarity and completeness"
#}
# Should also print diagnostic information to STDERR
python -m coverage run --append tasklifo.py llmpush \
  --api-key $API_KEY \
  --base-url $BASE_URL \
  --model $MODEL \
  --message "$(cat README.md)" \
  --message "I have to polish this readme" \
  README.md
  
# Replace $SHA1 with actual SHA-1 of README.md
# Should print first few lines of README.md
python -m coverage run --append tasklifo.py checkout $SHA1 | head
```

### Coverage Visualization

```bash
python -m coverage html
```

Then view `tasklifo_py.html` inside your browser.

## Explanation of Logo

This logo is not a logo. It wears the posture of a crest, yet rejects the entire Western European grammar of heraldry:

No cross, no shield, no lions or eagles.

Instead: the North Asian cosmology of five colors and five directions:

- East - Electric Blue (`#7df9ff`): Python, creation and vitality.
- West - White (`#ffffff`): Ollama, wisdom and guardianship.
- South - Electric Red (`#e60000`): Git, flow and collaboration.
- North - Black (`#000000`): Bash, depth and command.
- Center - Electric Amber (`#ffbf00`): JSON, simplicity and fidelity.

The motto "与时偕行 / Tempus Sequi" is not in solemn Latin, but in `#` - at once a Markdown header, a satire of pompous mottos, and a mark of today's hashtag culture.

This is, thoroughly, a parody - of heraldry's authority, of its empty solemnity.

And also, a reconstruction - a new cosmogram of time and code, guarded by modern mascots.

## Contributing

Contributions are welcome! Please submit pull requests or open issues on the GitHub repository.

## License

This project is licensed under the [AGPL-3.0 License](LICENSE).