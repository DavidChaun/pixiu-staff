from flask import Flask, request
from answer import get_answer

app = Flask(__name__)


@app.route('/chat')
def chat():
    question = request.args.get('question', None)
    answer = get_answer(question)
    return f'Listen, my answer is: \n {answer}'


if __name__ == '__main__':
    app.run()
