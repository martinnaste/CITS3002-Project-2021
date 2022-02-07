import socket 
import sys
from tkinter.constants import CURRENT
import tiles
import threading
import time
import queue
import random

board = tiles.Board()
ACTIVECONNECTIONS = []
LOBBYCLIENTS = []


#Stored - Idnum is the key, value is an array [connection, name]
#NAMES[idnum][0] = connection
#NAMES[idnum][1] = name
NAMES = {}

ACTIVELOBBYCONNS = []
ELIMINATED = -2 

HANDLERQUEUE = queue.Queue()
PLAYERTURN = queue.Queue()
CURRPLAYER = -1

mylock = threading.Lock() #lock for each group of things i am assigning
globalsLock = threading.Lock()

def get_random_players():
  #get the frist up to four in active connections into temp array
  #remove 1st and add to end, up to 4 times
  #shuffle temp array, then put each item in by that shuffled order into player queue
  number = 0
  if (len(ACTIVECONNECTIONS) > 1):
    number = 2
    if (len(ACTIVECONNECTIONS) > 2):
      number = 3
      if (len(ACTIVECONNECTIONS) > 3):
        number = 4 
  
  TempList = []
  if number == 2:
    for i in range(number):
      with globalsLock:
        TempList.append(ACTIVECONNECTIONS[0])
        ACTIVECONNECTIONS.pop(0)
        ACTIVECONNECTIONS.append(TempList[i])
  elif number > 2:
    #get random connection from active connections  up to 4 times
    while len(TempList) != number:
      with globalsLock:
        randPlayer = random.choice(ACTIVECONNECTIONS)
        if(randPlayer not in TempList):
          TempList.append(randPlayer)
  random.shuffle(TempList)

  return TempList

def start_game():
  global CURRPLAYER, ELIMINATED, LOBBYCLIENTS
  with globalsLock:
    ELIMINATED = 0
  shufflist = get_random_players()
  for num, details in NAMES.items():
    conn, name = details
    for item in shufflist:
      if(conn == item):
        with globalsLock:
          ACTIVELOBBYCONNS.append(num)
          LOBBYCLIENTS.append(num)
          PLAYERTURN.put(num)
    try:
      conn.sendall(tiles.MessageGameStart().pack())
    except:
      pass
    if(num in ACTIVELOBBYCONNS):
      for _ in range(tiles.HAND_SIZE):
        tileid = tiles.get_random_tileid()
        if(conn in ACTIVECONNECTIONS):
          try:
            conn.sendall(tiles.MessageAddTileToHand(tileid).pack())
          except:
            pass
            # print('error here')
  with globalsLock:
    CURRPLAYER = PLAYERTURN.get()
  for num, details in NAMES.items():
    conn, name = details
    try:
      conn.sendall(tiles.MessagePlayerTurn(CURRPLAYER).pack())
    except:
      pass
  with globalsLock:
    PLAYERTURN.put(CURRPLAYER)

  

def client_manager():
  while True:
    global CURRPLAYER, ELIMINATED, LOBBYCLIENTS
    idnum, event = HANDLERQUEUE.get()

    if event == 'Joined':
      #every new player joined gets a message from all other players
      for num, details in NAMES.items():
        conn, name = details
        if(num != idnum):
          try:
            NAMES[idnum][0].sendall(tiles.MessagePlayerJoined(name, num).pack())
          except:
            pass 
      for num, details in NAMES.items():
        conn, name = details
        if(num != idnum):
          try:
            NAMES[num][0].sendall(tiles.MessagePlayerJoined(NAMES[idnum][1], idnum).pack())
          except:
            pass
      if(len(ACTIVECONNECTIONS) >= 2 and CURRPLAYER == -1): #and there is no game running
        start_game()

      if(idnum not in ACTIVELOBBYCONNS and CURRPLAYER != -1):
        for num in ACTIVELOBBYCONNS:
          try:
            NAMES[idnum][0].sendall(tiles.MessagePlayerTurn(num).pack())
          except:
            pass
        try:
          NAMES[idnum][0].sendall(tiles.MessagePlayerTurn(CURRPLAYER).pack())
        except:
          pass
        for i in range(0,5):
          for j in range(0,5):
            id, rotation, placerId = board.get_tile(i, j)
            if(id != None and rotation != None and placerId != None):
              try:
                NAMES[idnum][0].sendall(tiles.MessagePlaceTile(idnum, id, rotation, i, j).pack())
              except:
                pass
        for num in ACTIVELOBBYCONNS:
          if(board.have_player_position(num)):
            x, y, pos = board.get_player_position(num)
            try:
              NAMES[idnum][0].sendall(tiles.MessageMoveToken(num, x, y, pos).pack())
            except:
              pass
          if num not in LOBBYCLIENTS:
            try:
              NAMES[idnum][0].sendall(tiles.MessagePlayerEliminated(num).pack())
            except:
              pass

    elif event == 'Disconnected':
      print('omg {} disconnected'.format(idnum))
      print('ALC {}, LC {}'.format(ACTIVELOBBYCONNS, LOBBYCLIENTS))
      print('AC {}'.format(ACTIVECONNECTIONS))
      print('ELIMINATED {}, PLAYERTURN {}, CURRPLAYER {}'.format(ELIMINATED, list(PLAYERTURN.queue), CURRPLAYER))
      # if(idnum == CURRPLAYER):
      # print('id == currplayer')
      tempQ = queue.Queue()
      with mylock:
        for item in ACTIVELOBBYCONNS:
          if item != idnum:
            tempQ.put(item)
        if(idnum in ACTIVELOBBYCONNS):
          ELIMINATED+=1
        if idnum in ACTIVELOBBYCONNS:
          ACTIVELOBBYCONNS.remove(idnum)
        conn = NAMES[idnum][0]
        if conn in ACTIVECONNECTIONS:
          ACTIVECONNECTIONS.remove(conn)
        if idnum in LOBBYCLIENTS:
          LOBBYCLIENTS.remove(idnum)
        for i in range(len(list(PLAYERTURN.queue))):
          PLAYERTURN.get()
        for i in range(len(ACTIVELOBBYCONNS)):
          player = tempQ.get()
          PLAYERTURN.put(player)
        NAMES.pop(idnum)

        for num, details in NAMES.items():
          conn, name = details
          if(conn in ACTIVECONNECTIONS):
            try:
              conn.sendall(tiles.MessagePlayerEliminated(idnum).pack())
            except:
              pass
        #if there are only two players left then end the game and wipe the board and wait for more clients
        if((ELIMINATED == (len(ACTIVELOBBYCONNS) - 1)) or ((len(ACTIVELOBBYCONNS) == 1) and len(ACTIVECONNECTIONS) >=2)):
          #change current player to null etc
          # start end game process
          with globalsLock:
            CURRPLAYER = -1
            ELIMINATED = -2
            ACTIVELOBBYCONNS.clear()
            LOBBYCLIENTS.clear()
            with PLAYERTURN.mutex:
              PLAYERTURN.queue.clear()

            board.reset()

          if(len(ACTIVECONNECTIONS)>=2 and CURRPLAYER == -1):
            start_game()
        else:
          CURRPLAYER = PLAYERTURN.get()
          PLAYERTURN.put(CURRPLAYER)
      pass
    elif isinstance(event, tiles.MessagePlaceTile):
      if idnum == CURRPLAYER and (len(ACTIVELOBBYCONNS) >=2):
        if board.set_tile(event.x, event.y, event.tileid, event.rotation, event.idnum): 
          # notify client that placement was successful
          for num, details in NAMES.items():
            conn, name = details
            try:
              conn.sendall(event.pack())# send to all players so they can see the change
            except:
              pass
# UPDATE TILES??!!!!
          # check for token movement
          positionupdates, eliminated = board.do_player_movement(LOBBYCLIENTS)

          for event in positionupdates:
            for num, details in NAMES.items():
              conn, name = details
              try:
                conn.sendall(event.pack()) # send that to all players
              except:
                pass

          for num1, details1 in NAMES.items(): #LOCKS with globals
            conn1, name1 = details1
            if num1 in eliminated: # AND IF NUM1 iS NOT IN NEW GLOBAL LOBBYCLIENTS?
              with globalsLock:
                if num1 in LOBBYCLIENTS:
                  ELIMINATED+=1
                  LOBBYCLIENTS.remove(num1)
                  tempQ = queue.Queue()
                  for item in LOBBYCLIENTS:
                    if item != num1:
                      tempQ.put(item)
                  for i in range(len(list(PLAYERTURN.queue))): #maybe get curr player first then do the thing, save it then add it first then others if not match
                    PLAYERTURN.get()
                  for i in range(len(LOBBYCLIENTS)):
                    player = tempQ.get()
                    PLAYERTURN.put(player)
                  for num, details in NAMES.items():
                    conn, name = details
                    try:
                      conn.sendall(tiles.MessagePlayerEliminated(num1).pack())
                    except:
                      pass

          # pickup a new tile
          tileid = tiles.get_random_tileid()
          try:
            NAMES[idnum][0].sendall(tiles.MessageAddTileToHand(tileid).pack()) #stays the same becuase were only sending it to the player who put a tile down
          except:
            pass

          # start next turn
          with globalsLock:
            tempNextCurr = PLAYERTURN.get()
            for num, details in NAMES.items():
              conn, name = details
              try:
                conn.sendall(tiles.MessagePlayerTurn(tempNextCurr).pack())#pick next idnum, and send to all players. global to hold current player turn
              except:
                pass
            CURRPLAYER = tempNextCurr
            PLAYERTURN.put(CURRPLAYER)

    elif isinstance(event, tiles.MessageMoveToken):
      if idnum == CURRPLAYER and (len(ACTIVELOBBYCONNS) >=2):
        if not board.have_player_position(event.idnum):
            if board.set_player_start_position(event.idnum, event.x, event.y, event.position):
              # check for token movement
              positionupdates, eliminated = board.do_player_movement(LOBBYCLIENTS)

              for event in positionupdates:
                for num, details in NAMES.items():
                  conn, name = details
                  try:
                    conn.sendall(event.pack()) #send to everyone
                  except:
                    pass
              
              for num1, details1 in NAMES.items():
                conn1, name1 = details1
                if num1 in eliminated:
                  with globalsLock:
                    if num1 in LOBBYCLIENTS:
                      ELIMINATED+=1
                      LOBBYCLIENTS.remove(num1)
                      tempQ = queue.Queue()
                      for item in LOBBYCLIENTS:
                        if item != num1:
                          tempQ.put(item)
                      for i in range(len(list(PLAYERTURN.queue))): #maybe get curr player first then do the thing, save it then add it first then others if not match
                        PLAYERTURN.get()
                      for i in range(len(LOBBYCLIENTS)):
                        player = tempQ.get()
                        PLAYERTURN.put(player)
                      for num, details in NAMES.items():
                        conn, name = details
                        try:
                          conn.sendall(tiles.MessagePlayerEliminated(num1).pack())
                        except:
                          pass

              # start next turn
              # if( game has not ended):
              with globalsLock:
                tempNextCurr = PLAYERTURN.get()
                for num, details in NAMES.items():
                  conn, name = details
                  try:
                    conn.sendall(tiles.MessagePlayerTurn(tempNextCurr).pack())#pick next idnum, and send to all players. global to hold current player turn
                  except:
                    pass
                CURRPLAYER = tempNextCurr
                PLAYERTURN.put(CURRPLAYER)

    if((ELIMINATED == (len(ACTIVELOBBYCONNS) - 1))):
      #change current player to null etc
      # start end game process
      with globalsLock:
        CURRPLAYER = -1
        ELIMINATED = -2
        ACTIVELOBBYCONNS.clear()
        LOBBYCLIENTS.clear()
        with PLAYERTURN.mutex:
          PLAYERTURN.queue.clear()

        board.reset()

      if(len(ACTIVECONNECTIONS)>=2 and CURRPLAYER == -1):
        start_game()

    HANDLERQUEUE.task_done()     
      
def client_handler(connection, address):
  host, port = address
  name = '{}:{}'.format(host, port)
  
  with mylock:
    idnum = threading.get_ident()
    NAMES[idnum] = [connection, name]
    ACTIVECONNECTIONS.append(connection)
  #WRAP THESE IN TRY EXCEPTS
  try:
    connection.sendall(tiles.MessageWelcome(idnum).pack())
  except:
    pass

  with globalsLock:
    HANDLERQUEUE.put((idnum, 'Joined'))

  buffer = bytearray()

  while True: 
  #   if(CURRPLAYER != -1):#remov
  #     if(CURRPLAYER == idnum):#remove 
    try:
      chunk = connection.recv(4096)
      if not chunk:
        print('client {} disconnected'.format(address))
        with mylock:
          HANDLERQUEUE.put((idnum, 'Disconnected'))
          connection.close()
        return #change current player turn, remove this idnum from list
    except:
      pass
    buffer.extend(chunk)

    while True:
      msg, consumed = tiles.read_message_from_bytearray(buffer)
      if not consumed:
        break

      buffer = buffer[consumed:]

      print('received message {}'.format(msg))
      #if not your turn then dont send
      #do turn checks here
      if(CURRPLAYER != -1):
        if(CURRPLAYER == idnum):
          with globalsLock:
            HANDLERQUEUE.put((idnum, msg))


def start():
  # create a TCP/IP socket
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

  # listen on all network interfaces
  server_address = ('', 30020) 
  sock.bind(server_address)

  print('listening on {}'.format(sock.getsockname()))

  sock.listen(5)

  managerThread = threading.Thread(target=client_manager, daemon=True)
  managerThread.start()

  while True:
    # handle each new connection independently
    connection, client_address = sock.accept()
    print('received connection from {}'.format(client_address))
    thread = threading.Thread(target=client_handler, args=(connection, client_address), daemon=True)
    thread.start()

print("[STARTING] server is starting...")
start()