'''В этом файле содержатся все тексты сообщений и кнопок для каждого хэндлера'''
from aiogram.types import (
    InputRichBlockParagraph,
    RichTextBold,
    RichTextUnderline,
    RichTextItalic,
    RichTextUrl
)


class AlchemistBot:
    FULL_DESCRIPTION = (
        "Hello, I'm the Alchemist!🧪🧑‍🔬🧪🧑‍🔬🧪🧑‍🔬\nI can help you "
        "transfer the different colored liquids into your flasks so "
        "that you get flasks with liquids filtered by color.\n"
        "I can work with pictures so you don't have to fill the "
        "flasks completely by hand, and I can also change the level "
        "a little by adding an empty flask if your level cannot be "
        "solved with two empty flasks😊"
    )

    SHORT_DESCRITPION = (
        "Alchemist - telegram bot for solving your levels for games "
        "with transfusion of colored liquids"
    )


class KeyboardTexts:
    OPEN_REPOSITORY = "📖Open repository"

    CLUE_RESTART = "🔄️Restarting me"

    CLUE_ACCOUNT = "📒Your account"

    CLUE_TERMS = "📃Terms of use me"

    CLUE_SUPPORT = "❓Support from my developer"

    START_SOLVING = "🚀Start solving"

    RULES = "📝Rules of use"

    ACCOUNT = "📒Account"

    TERMS = "📃User Agreement"

    SUPPORT = "❓Support"

    CONTINUE = "⏭️Continue solving"

    BUY_ATTEMPTS = "🎟️Buy attempts"

    UPLOAD_IMAGE = "📩🖼️Upload new image"

    FEEDBACK = "Feedback to me🙃"

    RELOAD_IMAGE = "🔄️🖼️Reload image"

    ADD_SEGMENT = "➕🧪Add 1/4 flask"

    BUY_5_ATTEMPTS = "💰Buy 5🎟️ for 50⭐"

    BUY_12_ATTEMPTS = "💰Buy 12🎟️ for 100⭐"

    BUY_20_ATTEMPTS = "💰Buy 20🎟️ for 150⭐"

    BUY_UNLIM_ATTEMPTS = "💰Buy unlimited🎟️ for 350⭐"

    CANCEL = "❌Cancel"

    ACCEPT = "✅I understand"

    CONFIRM = "👌Confirm"

    CHANGE_COLOR = "🔁Change color"

    REMOVE_FLASK = "➖🧪Remove excess flask"

    MANUALLY = "🙍‍♂️Manually"

    AUTOFILL = "🤖Autofill"

    NEXT_OPTION = "➡️Next option"

    PREVIOUS_OPTION = "⬅️Previous option"

    SELECT = "✅Confirm selection"

    PAY_50 = "💰Pay 50⭐"

    PAY_100 = "💰Pay 100⭐"

    PAY_150 = "💰Pay 150⭐"

    PAY_350 = "💰Pay 350⭐"


class ExcuseMeTexts:
    EXCUSE_MESSAGE = [
        InputRichBlockParagraph(
            text=[
                "Unfortunately, due to stricter laws regarding the processing ",
                "of user's personal data in the Russian Federation, I can no ",
                "longer work with Russian users and be confident that I am ",
                "complying with the law.😞"
            ]
        ),
        InputRichBlockParagraph(
            text=[
                "However, since I cannot identify you as a citizen of Russia or ",
                "any other country (I do not collect any data that could help ",
                "with identification), I am forced to stop working with all ",
                "users. Thank you for using me, and I hope I helped you complete ",
                "some challenging levels for your game!🙂"
            ]
        ),
        InputRichBlockParagraph(
            text=[
                RichTextBold(text="Note from the developer: "),
                "This bot is an open-source project, so you are welcome to run, ",
                "use, and modify it as you wish, good luck!"
            ]
        ),
        InputRichBlockParagraph(
            text=(
                "Click the button below to open the project repository👇"
            )
        )
    ]


class SendWelcomeTexts:
    CONDITION_TEXT_FREE = [
        InputRichBlockParagraph(
            text=[
                "Every month I will give you unlimited free 🎟️. ",
                "You can see all the information in your account"
            ]
        ) 
    ]

    CONDITION_TEXT = [
        InputRichBlockParagraph(
            text=[
                "Every month I'll give you 5 free 🎟️ and 1 bonus free 🎟️ ",
                "for every third unsuccessful attempt to find a solution ",
                "(unless you have activated unlimited 🎟️ for 30 days), ",
                "if they are not enough for you, you can buy more for a ",
                "small fee. You can see all the information in your account"
            ]
        )
    ]

    READ_RULES = [
        InputRichBlockParagraph(
            text=[
                "Hello, ",
                RichTextBold(text="{first_name}"),
                "😁"
            ]
        ),
        InputRichBlockParagraph(
            text=[
                "If this is your first time interacting with me, I strongly ",
                "recommend that you read about some rules that you need to ",
                "follow to work correctlyby clicking the button below👇"
            ]
        )
    ]

    GET_STARTED = [
        InputRichBlockParagraph(
            text=[
                "If this is not the first time you have done this, then I just ",
                "remind you that to restart me, you can enter the /start ",
                "command."
            ]
        )
    ]


class StartSolvingTexts:
    OUT_ATTEMPTS = [
        InputRichBlockParagraph(text="Sorry, you've run out of attempts😞"),
        InputRichBlockParagraph(
            text=[
                "If you want to continue now, you can buy multiple attempts ",
                "for a small fee"
            ]
        )
    ]

    START_SOLVING_FRIEND = [
        InputRichBlockParagraph(text="So let's get started😎"),
        InputRichBlockParagraph(text="Upload the screenshot as an image, please"),
        InputRichBlockParagraph(text="Now you have an unlimited 🎟️")
    ]

    START_SOLVING_UNLIM = [
        InputRichBlockParagraph(text="So let's get started😎"),
        InputRichBlockParagraph(text="Upload the screenshot as an image, please"),
        InputRichBlockParagraph(text="Now you have an unlimited 🎟️"),
        InputRichBlockParagraph(
            text=[
                "*Unlimited is available within 30 days from the date of ",
                "payment"
            ]
        )
    ]

    START_SOLVING_FREE_PAID = [
        InputRichBlockParagraph(text="So let's get started😎"),
        InputRichBlockParagraph(text="Upload the screenshot as an image, please"),
        InputRichBlockParagraph(text="Now you have:"),
        InputRichBlockParagraph(text="Free 🎟️: {free_attempts}"),
        InputRichBlockParagraph(text="Paid 🎟️: {paid_attempts}")
    ]

    START_SOLVING_FREE = [
        InputRichBlockParagraph(text="So let's get started😎"),
        InputRichBlockParagraph(text="Upload the screenshot as an image, please"),
        InputRichBlockParagraph(text="Now you have:"),
        InputRichBlockParagraph(text="Free 🎟️: {free_attempts}")
    ]

    START_SOLVING_PAID = [
        InputRichBlockParagraph(text="So let's get started😎"),
        InputRichBlockParagraph(text="Upload the screenshot as an image, please"),
        InputRichBlockParagraph(text="Now you have:"),
        InputRichBlockParagraph(text="Paid 🎟️: {paid_attempts}")
    ]

    RULES = [
        InputRichBlockParagraph(
            text=[
                "🙋‍♂️Now I'll tell you a little more about myself so that you ",
                "know how to interact with me correctly. This is very ",
                "important, because if you follow these few simple rules, you ",
                "will get more accurate recognition of the colors inside the ",
                "flasks, as well as the correct solutions for your specific ",
                "level"
            ]
        ),
        InputRichBlockParagraph(text="Now a few words about the functionality:"),
        InputRichBlockParagraph(
            text=[
                "✔️When you upload a screenshot, you need to upload it as a ",
                "picture, not as a file, that is, in a chat with me, I should ",
                "see your message as a full-fledged picture, about half the ",
                "screen"
            ]
        ),
        InputRichBlockParagraph(
            text=[
                "✔️The screenshot does not need to be cropped or compressed in ",
                "any way, I will do it myself, so just send me the original ",
                "image"
            ]
        ),
        InputRichBlockParagraph(
            text=[
                "✔️",
                RichTextUnderline(
                    text=RichTextBold(
                        text=[
                            "IF YOU USUALLY USE PATTERN MODE, PLEASE TURN IT OFF ",
                            "BEFORE TAKING A SCREENSHOT"
                        ]
                    )
                ),
                "and sending it to me, I'm not good at recognizing shapes inside ",
                "colored rectangles, so I won't be able to recognize your level ",
                "accurately (maybe I'll learn this in the future!)"
            ]
        ),
        InputRichBlockParagraph(
            text=[
                "✔️Upload me an image with the initial position of the colors ",
                "in the flasks, this is the only way I can find a solution"
            ]
        ),
        InputRichBlockParagraph(
            text=[
                "That's probably all the subtleties that I wanted to tell you ",
                "about working with me, good luck!🤞🤞🤞"
            ]
        )
    ]

    BUY_ATTEMPTS = [
        InputRichBlockParagraph(text="You can choose one of the following offers for purchase")
    ]

    ERROR_ACTION_FREE = [
        InputRichBlockParagraph(
            text=[
                "To get started, click the ",
                RichTextBold(text="🚀Start solving "),
                "button, please"
            ]
        )
    ]

    ERROR_ACTION = [
        InputRichBlockParagraph(
            text=[
                "To get started, click the ",
                RichTextBold(text="🚀Start solving "),
                "button or buy attempts by clicking the ",
                RichTextBold(text="🎟️Buy attempts "),
                "button, please"
            ]
        )
    ]


class GetImageTexts:
    UPLOAD_ERROR = [
        InputRichBlockParagraph(
            text=[
                "Something went wrong...🤷‍♂️ Please take a new screenshot of the ",
                "current level and upload it again or send another screenshot"
            ]
        )
    ]

    CAPTION = [
        InputRichBlockParagraph(
            text=[
                "This is what I saw in your screenshot. Compare the colors ",
                "here with the original image and please let me know if I was ",
                "successful so I can continue solving the problem. You can ",
                "also immediately add a blank segment if you deem it necessary ",
                "(in this case, the image is considered correctly recognized)! ",
                "If something is wrong, you can replace the incorrectly ",
                "recognized colors or delete the extra flask"
            ]
        )
    ]

    GET_IMAGE_ERROR = InputRichBlockParagraph(text="Send a 🖼️photo please")


class FillUndefinedColorsTexts:
    CHOOSE_FLASK = [
        InputRichBlockParagraph(
            text=[
                "Select the number of the flask you want to manipulate (count ",
                "the flask numbers from left to right, starting from the top ",
                "row, i.e. top row 1-6, middle row 7-12, bottom row 13-18)"
            ]
        )
    ]

    MANUALLY_FILLING = [
        InputRichBlockParagraph(
            text=[
                "Please select from the options provided the color that should ",
                "be in place of the green circle"
            ]
        )
    ]

    CHOOSE_SEGMENT = [
        InputRichBlockParagraph(
            text=[
                "Select the segment number in the flask to change the color ",
                "(segments are numbered from bottom to top, i.e. the bottom ",
                "segment of the flask is 1, and the top segment is 4)"
            ]
        )
    ]

    CHOOSE_COLOR = [
        InputRichBlockParagraph(text="Select a new color for the segment")
    ]

    SUCCESSFUL_REMOVAL_FLASK = [
        InputRichBlockParagraph(
            text=[
                "The flask removal was successful! Please choose your next ",
                "action"
            ]
        )
    ]

    SUCESSFUL_REPLACEMENT_COLOR = [
        InputRichBlockParagraph(text="Replacement successful! Please choose your next action")
    ]

    ERROR_ACTION = [
        InputRichBlockParagraph(
            text=[
                "Please select a color from above or choose what to do with ",
                "the image"
            ]
        )
    ]


class AutofillTexts:
    START_FIND_SOLUTION = [
        InputRichBlockParagraph(
            text=[
                "I'll look for a solution from this position. Wait, this may ",
                "take a while"
            ]
        )
    ]
    
    NOT_SOLVED = [
        InputRichBlockParagraph(
            text=[
                "😖😖😖I have looked through all {count_states} possible "
                "variants of pouring liquids and unfortunately, it is "
                "impossible to find a solution for this arrangement."
            ]
        ),
        InputRichBlockParagraph(
            text=[
                "If you want to change the order of undefined colors, click ",
                RichTextBold(text="🔄️🖼️Update image")
            ]
        ),
        InputRichBlockParagraph(
            text=[
                "If you know all the colors, but the solution is still not ",
                "found, then I can add another empty flask, for this click ",
                RichTextBold(text="➕🧪Add empty flask")
            ]
        ),
        InputRichBlockParagraph(
            text=[
                "Or you can upload a new image, for this click ",
                RichTextBold(text="📩🖼️Upload new image")
            ]
        )
    ]

    SUCCESSFUL_SOLVED = [
        InputRichBlockParagraph(text="Yay!🥳🥳🥳I found a solution for you!!!🥳🥳🥳"),
        InputRichBlockParagraph(text="Let me know if you want a solution for another screenshot😁")
    ]

    BAD_IMAGE = [
        InputRichBlockParagraph(text="Unfortunately, no solution can be found for this image😞"),
        InputRichBlockParagraph(
            text=[
                "Please resubmit the screenshot and carefully check that all ",
                "colors are recognized correctly and in the correct positions"
            ]
        )
    ]

    OUT_ATTEMPTS = StartSolvingTexts.OUT_ATTEMPTS
    
    RELOAD_FREE_PAID = [
        InputRichBlockParagraph(text="Now you have:"),
        InputRichBlockParagraph(text="Free 🎟️: {free_attempts}"),
        InputRichBlockParagraph(text="Paid 🎟️: {paid_attempts}")
    ]

    RELOAD_FREE = [
        InputRichBlockParagraph(text="Now you have:"),
        InputRichBlockParagraph(text="Free 🎟️: {free_attempts}")
    ]

    RELOAD_PAID = [
        InputRichBlockParagraph(text="Now you have:"),
        InputRichBlockParagraph(text="Paid 🎟️: {paid_attempts}")
    ]

    SELECT_MODE = [
        InputRichBlockParagraph(
            text=[
                "Tell me if you want to fill in the undefined colors manually ",
                "or should I do it automatically?🙂"
            ]
        )
    ]

    SELECT_START_POSITION = [
        InputRichBlockParagraph(
            text=[
                "Click on one of the buttons below to get another option or ",
                "select the current option"
            ]
        )
    ]


class AccountTexts:
    FRIENDS_NOTE = [
            InputRichBlockParagraph(
            text=RichTextItalic(
                text=RichTextBold(text="❗You have an unlimited 🎟️ forever")
            )
        )
    ]

    HEADER = [
        InputRichBlockParagraph(text=RichTextBold(text="🔐Your personal account")),
        InputRichBlockParagraph(
            text=[
                RichTextBold(text="👤Username: "),
                "{full_name}"
            ]
        ),
        InputRichBlockParagraph(
            text=[
                RichTextBold(text="🆔ID: "),
                "{id}"
            ]
        )
    ]

    FOOTTER = [
        InputRichBlockParagraph(text="You can continue by clicking one of the buttons below👇")
    ]

    FRIENDS_MESSAGE = HEADER + [
        InputRichBlockParagraph(
            text=[
                RichTextBold(text="Free 🎟️: ")
            ]
        )
    ] + FRIENDS_NOTE + FOOTTER

    USERS_NOTE = [
        InputRichBlockParagraph(
            text=RichTextItalic(
                text=RichTextBold(
                    text=[
                        "❗Free 5 attempts are restored on the first of every ",
                        "month"
                    ]
                )
            )
        )
    ]

    TIMEOUT_UNLIM = "🗓️Unlimited plan end date: {end_unlimited}"

    USERS_MESSAGE = HEADER + [
        InputRichBlockParagraph(
            text=[
                RichTextBold(text="Free 🎟️: "),
                "{free_attempts}"
            ]
        )
    ] + USERS_NOTE + [
        InputRichBlockParagraph(
            text=[
                RichTextBold(text="Paid 🎟️: "),
                "{paid_attempts}"
            ]
        ),
        InputRichBlockParagraph(text=RichTextItalic(text=RichTextBold(text="{added_text}")))
    ] + FOOTTER


class CheckUpdatesTexts:
    RESTART_MESSAGE = [
        InputRichBlockParagraph(
            text=[
                "I have received important updates, to continue using me ",
                "please restart me by typing /start🙂"
            ]
        )
    ]


class PaymentTexts:
    BUY_5_ATTEMPTS = "Please pay for 5🎟️"

    BUY_12_ATTEMPTS = "Please pay for 12🎟️"

    BUY_20_ATTEMPTS = "Please pay for 20🎟️"

    BUY_UNLIM_ATTEMPTS = (
        "Please pay for unlimited 🎟️ (unlimited is available within 30 "
        "days from the date of payment)"
    )

    SUCCESSFUL_UNLIM = [
        InputRichBlockParagraph(text="Payment was successful, you now have unlimited 🎟️."),
        InputRichBlockParagraph(
            text=[
                "Click the button below if you want to start or continue the ",
                "solution"
            ]
        )
    ]

    SUCCESSFUL_PAYMENT = [
        InputRichBlockParagraph(
            text=[
                "Payment was successful, you now have {paid_attempts} ",
                "purchased 🎟️."
            ]
        ),
        InputRichBlockParagraph(
            text=[
                "Click the button below if you want to start or continue the ",
                "solution"
            ]
        )
    ]

    OUT_ATTEMPTS = StartSolvingTexts.OUT_ATTEMPTS


class LabelsForPrices:
    SMALL_PACK = "5 attempts"

    MIDDLE_PACK = "12 attempts"

    BIG_PACK = "20 attempts"

    UNLIM_PACK = "Unlimited attempts"


class SupportTexts:
    SUPPORT = [
        InputRichBlockParagraph(
            text=[
                "If you got here, it means you still needed advice from my ",
                "developer, I'm very sorry that this happened😞"
            ]
        ),
        InputRichBlockParagraph(
            text=[
                "I hope that together you can solve your problem as soon as ",
                "possible🙏"
            ]
        ),
        InputRichBlockParagraph(
            text=[
                "In order to contact my developer you just need to click on ",
                "the button below and he'll answer you within a day, good ",
                "luck✊"
            ]
        )
    ]


class TermsTexts:
    TERMS = [
        InputRichBlockParagraph(
            text=[
                "By starting to work with me you agree to the ",
                RichTextUrl(
                    text="User Agreement",
                    url="https://just-russian-amateur.github.io/terms_for_alchemist_bot/Terms_of_Service.html"
                ),
                " and ",
                RichTextUrl(
                    text="Privacy Policy",
                    url="https://just-russian-amateur.github.io/terms_for_alchemist_bot/Privacy_Policy.html",
                ),
                "You can ask my developer any questions you have regarding the ",
                "operation of the bot or the payment system through the feedback ",
                "system using the command /support🙂"
            ]
        ),
        InputRichBlockParagraph(
            text=[
                "After clicking the button below you can continue from where you ",
                "left off"
            ]
        )
    ]