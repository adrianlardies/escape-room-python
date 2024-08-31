import json
import time
import sys


RANKING_FILE = 'ranking.json'


# Temporizador (en segundos)
TIMER_DURATION = 300  # 5 minutos


# Inicialización del tiempo de inicio
start_time = time.time()


def linebreak():
    """
    Imprime un salto de línea doble para separar visualmente secciones en la salida de la consola.
    Esto se utiliza principalmente para mejorar la legibilidad del texto que se muestra al jugador.
    """

    print("\n\n")


def start_game(game_state, init_game_state):
    """
    Inicia el juego y el temporizador. Muestra el mensaje inicial al jugador y 
    entra en un bucle donde se juega la partida hasta que se termine.
    
    Args:
    - game_state: Estado actual del juego.
    - init_game_state: Estado inicial del juego que se utilizará para reiniciar si es necesario.
    """

    global start_time
    start_time = time.time()  # Reiniciar el temporizador cuando se inicia el juego
    print("Te despiertas en un sofá y te encuentras en una casa extraña sin ventanas en la que nunca has estado antes. No recuerdas por qué estás aquí ni qué sucedió antes. Sientes que se acerca un peligro desconocido y debes salir de la casa, ¡AHORA!")

    game_ongoing = True
    while game_ongoing:
        game_ongoing = play_room(game_state, game_state["current_room"], init_game_state)


def play_room(game_state, room, init_game_state):
    """
    Controla la lógica principal de la partida mientras el jugador explora una habitación. 
    Verifica si el jugador ha alcanzado la habitación objetivo, si el tiempo se ha agotado y 
    permite al jugador realizar acciones como explorar, examinar, etc.
    
    Args:
    - game_state: Estado actual del juego.
    - room: Habitación en la que se encuentra el jugador actualmente.
    - init_game_state: Estado inicial del juego que se utilizará para reiniciar si es necesario.
    
    Returns:
    - bool: Retorna False si el juego ha terminado, True si continúa.
    """

    if check_time(game_state):
        game_state["current_room"] = room
        if game_state["current_room"] == game_state["target_room"]:
            print("¡Felicidades! ¡Escapaste de la habitación!")
            calculate_score()  # Calcular y mostrar la puntuación
            return False  # Indica que el juego ha terminado
        else:
            print("Ahora estás en " + room["name"])
            intended_action = input("¿Qué te gustaría hacer? Escribe 'explorar', 'examinar', 'salir', 'reiniciar', 'tiempo' o 'ranking'?").strip()
            if intended_action == "explorar":
                explore_room(game_state, room)
                return play_room(game_state, room, init_game_state)
            elif intended_action == "examinar":
                examine_item(game_state, input("¿Qué te gustaría examinar?").strip(), init_game_state)
                return play_room(game_state, room, init_game_state)
            elif intended_action == "salir":
                return quit_game()  # Termina el juego y devuelve False
            elif intended_action == "reiniciar":
                restart_game(game_state, init_game_state)
                return play_room(game_state, game_state["current_room"], init_game_state)
            elif intended_action == "tiempo":
                show_time_remaining()
                return play_room(game_state, room, init_game_state)
            elif intended_action == "ranking":
                show_ranking()
                return play_room(game_state, room, init_game_state)
            else:
                print("No estoy seguro de lo que quieres decir. Escribe 'explorar', 'examinar', 'salir', 'reiniciar', 'tiempo' o 'ranking'.")
                return play_room(game_state, room, init_game_state)
            linebreak()
    return True  # Continúa el juego


def explore_room(game_state, room):
    """
    Permite al jugador explorar la habitación actual y listar los objetos disponibles en ella.
    
    Args:
    - game_state: Estado actual del juego.
    - room: Habitación en la que se encuentra el jugador actualmente.
    """

    items = [i["name"] for i in game_state["object_relations"][room["name"]]]
    print("Exploras la habitación. Esta es " + room["name"] + ". Encuentras " + ", ".join(items))


def get_next_room_of_door(game_state, door, current_room):
    """
    Devuelve la próxima habitación conectada por una puerta desde la habitación actual.
    
    Args:
    - game_state: Estado actual del juego.
    - door: La puerta que conecta dos habitaciones.
    - current_room: La habitación actual en la que se encuentra el jugador.
    
    Returns:
    - dict: La habitación a la que la puerta conduce desde la habitación actual.
    """

    connected_rooms = game_state["object_relations"][door["name"]]
    for room in connected_rooms:
        if current_room != room:
            return room


def examine_item(game_state, item_name, init_game_state):
    """
    Permite al jugador examinar un objeto en la habitación actual. Dependiendo del tipo de objeto, 
    el jugador puede encontrar una llave, intentar abrir una puerta, etc.
    
    Args:
    - game_state: Estado actual del juego.
    - item_name: Nombre del objeto a examinar.
    - init_game_state: Estado inicial del juego que se utilizará para reiniciar si es necesario.
    """

    current_room = game_state["current_room"]
    next_room = ""
    output = None

    for item in game_state["object_relations"][current_room["name"]]:
        if item["name"] == item_name:
            output = "Examinas " + item_name + ". "
            if item["type"] == "door":
                have_key = False
                for key in game_state["keys_collected"]:
                    if key["target"] == item:
                        have_key = True
                if have_key:
                    output += "La desbloqueas con una llave que tienes."
                    next_room = get_next_room_of_door(game_state, item, current_room)
                else:
                    output += "Está cerrada, pero no tienes la llave."
            else:
                if item["name"] in game_state["object_relations"] and len(game_state["object_relations"][item["name"]]) > 0:
                    item_found = game_state["object_relations"][item["name"]].pop()
                    game_state["keys_collected"].append(item_found)
                    output += "Encuentras " + item_found["name"] + "."
                else:
                    output += "No hay nada interesante sobre esto."
            print(output)
            break

    if output is None:
        print("El objeto que pediste no se encuentra en la habitación actual.")

    if next_room:
        while True:
            response = input("¿Quieres ir a la siguiente habitación? Escribe 'sí' o 'no'").strip().lower()
            if response == 'sí':
                return play_room(game_state, next_room, init_game_state)
            elif response == 'no':
                return play_room(game_state, current_room, init_game_state)
            else:
                print("Respuesta no válida. Por favor, escribe 'sí' o 'no'.")
    else:
        return play_room(game_state, current_room, init_game_state)


def check_time(game_state):
    """
    Verifica si el tiempo límite del juego ha sido alcanzado. Si el tiempo ha terminado, 
    el juego termina. Si no, permite que el juego continúe.
    
    Args:
    - game_state: Estado actual del juego.
    
    Returns:
    - bool: Retorna True si el juego puede continuar, de lo contrario, termina el juego.
    """

    elapsed_time = time.time() - start_time
    if elapsed_time >= TIMER_DURATION:
        print("¡Se acabó el tiempo! No lograste escapar a tiempo.")
        sys.exit()  # Termina el juego si se acaba el tiempo
    return True


def show_time_remaining():
    """
    Muestra el tiempo restante antes de que termine el juego. Si el tiempo se agota mientras 
    se muestra, el juego termina.
    """

    elapsed_time = time.time() - start_time
    remaining_time = TIMER_DURATION - elapsed_time
    if remaining_time > 0:
        minutes, seconds = divmod(remaining_time, 60)
        print(f"Tiempo restante: {int(minutes)} minutos y {int(seconds)} segundos")
    else:
        print("¡Se acabó el tiempo! No lograste escapar a tiempo.")
        sys.exit()


def restart_game(game_state, init_game_state):
    """
    Reinicia el juego restaurando el estado inicial y reiniciando el temporizador. Luego, 
    vuelve a iniciar el juego desde el principio.
    
    Args:
    - game_state: Estado actual del juego.
    - init_game_state: Estado inicial del juego que se utilizará para reiniciar.
    """

    global start_time
    game_state.update(init_game_state)  # Restablecer estado inicial del juego
    start_time = time.time()  # Reiniciar el temporizador
    print("¡El juego ha sido reiniciado!")
    start_game(game_state, init_game_state)


def quit_game():
    """
    Finaliza el juego mostrando un mensaje de despedida y saliendo del programa.
    
    Returns:
    - bool: Retorna False para indicar que el juego ha terminado.
    """

    print("¡Gracias por jugar! El juego se cerrará en un momento...")
    time.sleep(2)  # Pausa de 2 segundos antes de terminar
    return False  # Indica que el juego ha terminado


def load_ranking():
    """
    Carga el ranking de jugadores desde un archivo JSON. Si el archivo no existe, 
    devuelve una lista vacía.
    
    Returns:
    - list: Lista de los rankings cargados.
    """

    try:
        with open(RANKING_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_ranking(ranking):
    """
    Guarda el ranking de jugadores en un archivo JSON.
    
    Args:
    - ranking: Lista de rankings a guardar.
    """

    with open(RANKING_FILE, 'w') as file:
        json.dump(ranking, file)


def update_ranking(player_name, score):
    """
    Actualiza el ranking con la puntuación del jugador actual, la guarda y 
    muestra los 10 mejores resultados.
    
    Args:
    - player_name: Nombre del jugador.
    - score: Puntuación obtenida por el jugador.
    """

    ranking = load_ranking()
    ranking.append({"name": player_name, "score": score, "time": time.time()})
    ranking = sorted(ranking, key=lambda x: x["score"], reverse=True)[:10]  # Mantén solo las 10 mejores puntuaciones
    save_ranking(ranking)


def show_ranking():
    """
    Muestra los 10 mejores rankings de jugadores. Si no hay rankings, 
    indica que aún no hay datos disponibles.
    """

    ranking = load_ranking()
    if ranking:
        print("Top 10 Rankings:")
        for idx, entry in enumerate(ranking, start=1):
            print(f"{idx}. {entry['name']} - {entry['score']} puntos")
    else:
        print("Aún no hay rankings disponibles.")


def calculate_score():
    """
    Calcula la puntuación del jugador basada en el tiempo que ha tardado en escapar. 
    Solicita el nombre del jugador, actualiza el ranking y lo muestra.
    """
    
    elapsed_time = time.time() - start_time
    score = 0

    if elapsed_time < 120:  # Menos de 2 minutos
        score = 100
    elif elapsed_time < 240:  # Entre 2 y 4 minutos
        score = 75
    elif elapsed_time < 300:  # Entre 4 y 5 minutos
        score = 50
    else:
        score = 0

    print(f"Tu puntuación es: {score} puntos!")

    # Solicitar el nombre del jugador y actualizar el ranking
    player_name = input("Introduce tu nombre para el ranking: ").strip()
    update_ranking(player_name, score)
    show_ranking()