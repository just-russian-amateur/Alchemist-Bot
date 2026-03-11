# Alchemist Bot

[EN](README.md) | [RU](README-RU.md)

## Preface

I decided to open source this project due to potential (and very likely) issues with **Telegram** in Russia, as well as potential problems with monetization, which could limit the bot's availability to Russian users. This step was taken to ensure that any interested user can run a local copy of the bot and use it as they see fit, without violating **the User Agreement** (linked in the **_all_my_texts.py_** file), **the laws of your country**, or **the Apache 2.0 license** selected for the current repository. I also hope that any interested user can contribute to the project's development and help fix bugs (if any are discovered), improve and expand the bot's functionality, or make other optimizations.

I would be very grateful!

## System Requirements

In this section, I will only list the recommended system requirements for the bot to ensure its stable and uninterrupted operation.

You can run the bot instance on a local PC or server, or on a VPS server from any cloud service provider.

### Recommended Requirements

* **CPU:** Intel or AMD, 1.8+ GHz, 1 core
* **OS:** Ubuntu 22.04+/Debian 10+
* **RAM:** 3+ GB
* **SSD:** 15+ GB (for a VPS server)/10+ GB of free space on a local PC or server
* **Network:** Any stable internet connection that doesn't block requests and responses to/from the Telegram Bot API (in Russia, local PCs and servers may experience issues; not yet applicable to VPS providers)
* **Interpreter:** Python 3.9+

This configuration is sufficient for both the bot and the installation of all necessary dependencies (discussed below).

## Installing Dependencies

The bot was written using the aiogram 3.x library and tested on Python 3.9 and 3.13, but should work equally well on all recent versions of the interpreter.

The bot requires three main components:

* [Git](https://git-scm.com/install/linux) - a distributed version control system.
* [Python interpreter](https://www.python.org/downloads/) with the following dependencies installed (installed via PIP):
  - aiogram;
  - opencv-python;
  - numpy;
  - redis;
  - apscheduler;
  - ultralytics;
  - dotenv;
  - some dependencies may need to be installed separately if they were not downloaded along with the ones listed above.
* Redis is an open-source NoSQL DBMS for storing user state in a state machine and user data. Installation and configuration of Redis are described on the [official website (users in Russia may require additional access to the site)](https://redis.io/docs/latest/get-started/).

**Note:** This bot uses a trained model based on [YOLOv11X](https://docs.ultralytics.com/models/yolo11/), which is available in this repository. However, the entire model could not be downloaded because it exceeded the 100 MB size limit. Therefore, to obtain this model, you need to install and configure not only [Git](https://git-scm.com/install/linux) but also [Git LFS](https://git-lfs.com/) to use Git for storing large files.

## A little about the project structure and files

**Note:** To create a bot copy, you need to register a new bot through the official bot **@BotFather** in **Telegram** and obtain a **token** for it. [You can see how to do this here](https://core.telegram.org/bots#how-do-i-create-a-bot).

The project structure is a hierarchical structure of logically separated functional blocks. The root of the project essentially contains system files and a generated image with example colors the bot can recognize, along with a sample environment file where the previously obtained token should be stored (for greater bot security). When using a real environment file, the **_.example_** postfix should not be present.

The bot structure itself looks like this:

```text
alchemist
├── callbacks/
│      └── all_my_callbacks.py
├── classes/
│      └── all_my_classes.py
├── handlers/
│      ├── account.py
│      ├── autofill.py
│      ├── check_updates.py
│      ├── fill_undefined_colors.py
│      ├── get_image.py
│      ├── payment.py
│      ├── send_welcome.py
│      ├── start_solving.py
│      ├── support.py
│      └── terms.py
├── keyboards/
│      └── all_my_keyboards.py
├── texts/
│      ├── all_my_texts.py
│      └── redis_keys.py
├── alchemist_bot.py
├── best.pt
├── config.py
├── found_colors.py
└── transfusion_of_liquids.py
```

The **_alchemist_bot.py_** file is the entry point for the bot. It includes a scheduler for monthly reset attempts, implements the command menu, and includes handlers. The **_config.py_** file stores most of the constants and initialization variables, and also loads the model. The **_found_colors.py_** file is used for processing screenshots.with user-generated game levels, and the **_transfusion_of_liquids.py_** file is designed to find a solution for the processed level from the screenshot.

The main logic of the bot's UI is handled by handlers, each of which is responsible for processing a specific bot state at the moment of user interaction. These handlers implement the bot's key logic, which includes processing available text commands, level screenshots, button presses, processing transactions in **Telegram Stars**, and accessing the database and the bot's state machine stored in **Redis**. You can learn more about what each handler does by viewing its source code.

**Note:** The bot also provides for the distribution of roles between regular users and "friends". It was implemented primarily to facilitate testing the bot for logical errors after making changes to the code, when testing is performed by several people. However, it can also be used to designate privileged users who will not be subject to the attempt limit (in case you plan to monetize the bot in some other way, for example, by introducing a subscription system).

**Note 2:** The payment processing handler can also be used as an example of working with the internal currency - **Telegram Stars**, since I haven't found many code examples for processing payments using this payment method yet.

## Bot Functionality and Capabilities

Currently, the bot's functionality includes the following:

* Recognition of flasks and a limited list of colors within them in images, including on complex backgrounds (when the background practically blends in with the contours or even the colors within the flasks; an example of a similar solution is demonstrated in the video below).
* Recognition of partially opened flasks in images (when one or more flask segments are hidden and were not revealed by the user as a result of pouring), and correct determination of the positions of open and hidden segments.
* Ability to manually fill hidden flask segments by selecting the appropriate color for each segment sequentially, even if not all color examples were revealed by the user (e.g., out of 14 flasks, 2 were empty and 12 flasks should have unique colors, but the user only revealed 10 unique colors).
* Ability to automatically fill hidden flask segments (recommended in most cases), including when not all unique colors were revealed (see the previous point).
* Ability to select precise automatic filling of hidden segments when the number of hidden segments is relatively small.
* Ability to replace any segment within any flask with any of the available colors that the bot can recognize (recommended when one or more colors were recognized incorrectly).
* Ability to add an empty segment before searching for a solution.
* Ability to delete any flask entirely (if the bot made an error(s) during recognition).
* Ability to select a different option for filling hidden segments without having to re-submit a screenshot.

## Usage Example

[Example of using the bot to solve one of the levels in a liquid-pouring game](https://youtube.com/shorts/1LuF7I0vwj4?si=c0fZsYv3RlSnkqTk)

## Conclusion

At this stage, the project is relatively complete. The bot has implemented a fairly broad and functional set of features. No critical bugs were found during testing, but this does not mean they are absent. If any are discovered, fixes can be implemented within a reasonable timeframe.
