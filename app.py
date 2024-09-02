from flask import Flask, render_template, request, redirect, url_for
from groq import Groq
import re
from markupsafe import Markup

# Initialize the Groq API client
api_token = "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"
model_llama318B = "llama-3.1-8b-instant"
model_llama38b8192="llama3-8b-8192"
client = Groq(api_key=api_token)

app = Flask(__name__)

# Store chat messages in a list (in-memory storage)
conversation = []


def beautify_response(response):
    """Clean and format the model response for display."""

    # Preserve paragraphs by replacing double newlines with <p> tags
    response = re.sub(r'\n\n+', '</p>\n<p>', response.strip())
    response = f'<p>{response}</p>'  # Add <p> tags at the beginning and end

    # Preserve code blocks
    response = re.sub(r'```(python|sql)(.*?)```', r'<pre><code class="\1">\2</code></pre>', response, flags=re.DOTALL)

    # Convert bullet points (lines starting with numbers followed by a period) to HTML list items
    response = re.sub(r'(?m)^\d+\.\s+', '<li>', response)
    response = re.sub(r'(?m)^\s*\n+', '</li>\n<li>', response)

    # Close the last list item and add list tags
    response = re.sub(r'(?m)(</li>)\s*$', '</li>', response)
    response = re.sub(r'(?m)(<li>.+?</li>)', '<ol>\n\\1\n</ol>', response)

    # Convert headings
    response = re.sub(r'^\s*([=-~]{3,})$', r'</p><h2>\1</h2><p>', response, flags=re.MULTILINE)
    response = re.sub(r'^#\s*(.*)', r'<h1>\1</h1>', response, flags=re.MULTILINE)
    response = re.sub(r'^##\s*(.*)', r'<h2>\1</h2>', response, flags=re.MULTILINE)

    # Format bold text
    response = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', response)

    # Clean up extra new lines
    response = re.sub(r'\n+', '\n', response)

    return Markup(response)

@app.route('/', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        user_message = request.form['message']
        if user_message:
            # Append the user message to the conversation list
            conversation.append({"role": "user", "content": user_message})

            # Send the entire conversation to the model
            chat_completion = client.chat.completions.create(
                messages=conversation,
                model=model_llama318B
            )

            # Get the model's response
            model_response = chat_completion.choices[0].message.content

            # Beautify and format the model response
            if isinstance(model_response, list):
                for item in model_response:
                    formatted_item = beautify_response(item)
                    conversation.append({"role": "assistant", "content": formatted_item})
            else:
                formatted_response = beautify_response(model_response)
                conversation.append({"role": "assistant", "content": formatted_response})

        # Redirect to the chat page to display the updated conversation
        return redirect(url_for('chat'))

    return render_template('chat.html', messages=conversation)

if __name__ == '__main__':
    app.run(debug=True)
