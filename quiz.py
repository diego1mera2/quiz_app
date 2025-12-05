import os
from random import shuffle
from flask import Flask, session, request, redirect, render_template, url_for
from db_scripts import get_question_after, get_quises, check_answer

def start_quiz(quiz_id):
    '''crea los valores deseados en el diccionario session'''
    session['quiz'] = quiz_id
    session['last_question'] = 0
    session['answers'] = 0
    session['total'] = 0

def end_quiz():
    session.clear()

def quiz_form():
    '''la función recibe una lista de cuestionarios de la base de datos y crea un formulario con una lista desplegable '''
    q_list = get_quises()
    return render_template('start.html', q_list=q_list)

def index():
    ''' Primera página: si vino con una solicitud GET, entonces seleccionar un cuestionario,
    si POST - entonces recordar el id del cuestionario y enviar las preguntas '''
    if request.method == 'GET':
        # el cuestionario no está seleccionado, restablecer el id del cuestionario y mostrar el formulario de selección
        start_quiz(-1)
        return quiz_form()
    else:
        # ¡se recibieron datos adicionales en la solicitud! Los usamos:
        quest_id = request.form.get('quiz') # número de cuestionario seleccionado 
        start_quiz(quest_id)
        return redirect(url_for('test'))

def save_answers():
    '''recibe datos desde el formulario, comprueba si la respuesta es correcta, escribe los resultados a la sesión'''
    answer = request.form.get('ans_text')
    quest_id = request.form.get('q_id')
    # esta pregunta ya se ha hecho:
    session['last_question'] = quest_id
    # aumenta el contador de pregunta:
    session['total'] += 1
    # comprueba si la respuesta coincide con el id correcto para esto
    if check_answer(quest_id, answer):
        session['answers'] += 1

def question_form(question):
    '''obtiene una fila de la base de datos correspondiente a la pregunta, devuelve el html con el formulario '''
    # pregunta - resultado de get_question_after
    # campos: 
            # [0] - número de pregunta del cuestionario, 
            # [1] - texto de la pregunta, 
            # [2] - respuesta correcta, [3],[4],[5] - respuestas incorrectas

    # mezclar las respuestas:
    answers_list = [
        question[2], question[3], question[4], question[5]
    ]
    shuffle(answers_list)
    # pasarlo a la plantilla, devolver el resultado:
    return render_template('test.html', question=question[1], quest_id=question[0], answers_list=answers_list)

def test():
    '''devuelve la página de la pregunta'''
    # ¿qué ocurriría si el usuario sin elegir un cuestionario fuera directamente a la dirección '/test'? 
    if not ('quiz' in session) or int(session['quiz']) < 0:
        return redirect(url_for('index'))
    else:
        # si recibimos datos, entonces necesitamos leerlos y actualizar la información:
        if request.method == 'POST':
            save_answers()
        # en cualquier caso, trabajar con el id de la pregunta actual
        next_question = get_question_after(session['last_question'], session['quiz'])
        if next_question is None or len(next_question) == 0:
            # las preguntas se terminaron:
            return redirect(url_for('result'))
        else:            
            return question_form(next_question)

def result():
    html = render_template('result.html', right=session['answers'], total=session['total'])
    end_quiz()
    return html

folder = os.getcwd() # recordar la carpeta de trabajo actual
# Crear un objeto de aplicación web:
app = Flask(__name__, template_folder=folder, static_folder=folder)  
app.add_url_rule('/', 'index', index, methods=['post', 'get'])   # crea una regla para la URL '/'
app.add_url_rule('/test', 'test', test, methods=['post', 'get']) # crea una regla para la URL '/test'
app.add_url_rule('/result', 'result', result) # crea una regla para la URL '/test'
# Establecer la clave de encriptación:
app.config['SECRET_KEY'] = 'ThisIsSecretSecretSecretLife'

if __name__ == "__main__":
    # Lanzar el servidor web:
    app.run()