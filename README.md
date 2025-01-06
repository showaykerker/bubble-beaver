# Bubble Beaver Discord Bot

A Discord bot that helps translate lyrics and messages from multiple artists using LLM capabilities.

## Features

- Multi-language translation support
- Artist-specific translation handling
- Customizable LLM prompts for different translation styles
- Docker containerization for easy deployment

## Requirements

- Python 3.9+
- Discord.py
- Docker
- Conda environment

## Setup

1. Create conda environment:
```bash
conda env create -f environment.yml
```

2. Activate the environment:
```bash
conda activate bubble-beaver
```

3. Set up your Discord bot token:
Create a `.env` file and add your Discord token:
```
DISCORD_TOKEN=your_token_here
OPENAI_API_KEY=your_openai_key_here
```

4. Build and run with Docker:
```bash
docker build -t bubble-beaver .
docker run -d --env-file .env bubble-beaver
```
Or run with Conda environment:
```bash
conda env create -f environment.yml
conda activate bubble-beaver
python main.py
```

## Flow Diagram
```mermaid
flowchart TB
    subgraph DB["Database"]
        direction TB
        subgraph Artist
            direction LR
            name
            prompt
            channelOrig
            channelEng
            channelZhTw
        end
        subgraph Messages
            direction LR
            timestamp
            artistId
            messageOrig
            messageEng
            messageZhTw
            messageDiscordId
            status
            error_reason
            retry_count
            context_order
            is_context_root
        end
        subgraph MessageContexts
            direction LR
            messageId
            context_group
            parent_message
        end
    end

    Start([Get message]) --artist--> LoadPrompts[Load Prompts]
    Start --msg--> CheckRoot{Check previous 24hr message}
    LoadPrompts --> FirstAttempt
    GeneralPrompt --> FirstAttempt
    
    CheckRoot --No Prev Msg--> NewGroup[Create New Group]
    CheckRoot --Has Prev Msg--> FirstAttempt

    FirstAttempt[LLM Translate] --Timeout/Error--> HandleError[Log Error]
    HandleError --retry < 3--> FirstAttempt
    HandleError --retry >= 3--> MarkFail
    
    FirstAttempt --Success--> ParseResponse{Parse JSON Response}
    ParseResponse --Invalid--> HandleError
    
    ParseResponse --Valid--> ContextCheck{"needs_context?"}
    ContextCheck --N--> SafetyCheck
    
    ContextCheck --Y--> SelectGroup[Select/Create Context Group]
    SelectGroup --> GetContext["Get n_required messages by context_order"]
    GetContext --> SecondAttempt[LLM Translate 2]
    SecondAttempt --> SafetyCheck
    
    SafetyCheck{Safety Check} --Unsafe--> ThirdAttempt[LLM Translate 3]
    SafetyCheck --Safe--> BackwardCheck
    
    ThirdAttempt --retry >= 3--> MarkFail[Mark Failed]
    ThirdAttempt --retry < 3--> SafetyCheck
    MarkFail --> SendFail[Send Fail Message]
    SendFail --> End([END])
    
    BackwardCheck{"Check msgs within\ncontext_group"} --N--> UpdateMsg[Update Message Status]
    BackwardCheck --Y--> UpdateCheck{Safety Check}
    
    UpdateCheck --Safe--> UpdatePrev[Update Previous Messages with msg discord Id]
    UpdateCheck --Unsafe--> UpdateMsg
    
    UpdatePrev --> UpdateMsg
    UpdateMsg --> Send[Send Message]
    Send --> End
```


## Usage

- `/mirror_channel <artist_name>` - Create mirror channels..
    - These channels will be served as a mirror of a single artist's messages.
    - Original Channel will be used to paste messages with the original language.
    - The bot will translate the messages to the target languages and paste them to channel mirrors.
    - This command will create 3 channels for the mirror with name `<artist_name>_original`, `<artist_name>_eng`, and `<artist_name>_zh-tw`.
- `/show <artist_name>` - Show the translation prompt for the artist.
- `/modify <artist_name>` - Modify the translation prompt for the artist. A textarea will show up with the current prompts.


## License

MIT License - See LICENSE file for details
