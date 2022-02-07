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
    print('we have 2 connections')
    if (len(ACTIVECONNECTIONS) > 2):
      number = 3
      print('we have 3 connections')
      if (len(ACTIVECONNECTIONS) > 3):
        number = 4  
        print('we have 4 connections')  
  
  print('[number] {}'.format(number))
  #print('[ACTIVECONNECTIONS] {}'.format(ACTIVECONNECTIONS))
  TempList = []
  if number == 2:
    for i in range(number):
      #print('[i] {} [TEMPLIST] {}'.format(i, TempList))
      #print('[ACTIVECONNECTIONS] {}'.format(ACTIVECONNECTIONS[0]))
      with globalsLock:
        TempList.append(ACTIVECONNECTIONS[0])
        ACTIVECONNECTIONS.pop(0)
        ACTIVECONNECTIONS.append(TempList[i])
      print('[TEMPLIST] 1 {}'.format(TempList))
  elif number > 2:
    #get random connection from active connections 4 times
    while len(TempList) != number:
      #print('[i] {} [TEMPLIST] {}'.format(i, TempList))
      #print('[ACTIVECONNECTIONS] {}'.format(ACTIVECONNECTIONS[0]))
      with globalsLock:
        randPlayer = random.choice(ACTIVECONNECTIONS)
        if(randPlayer not in TempList):
          TempList.append(randPlayer)
      # print('[TEMPLIST] 2 {}'.format(TempList))
  random.shuffle(TempList)
  # print('[TEMPLIST shuffle] {}'.format(TempList))

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
    conn.sendall(tiles.MessageGameStart().pack())
    if(num in ACTIVELOBBYCONNS):
      for _ in range(tiles.HAND_SIZE):
        tileid = tiles.get_random_tileid()
        if(conn in ACTIVECONNECTIONS):
          try:
            conn.sendall(tiles.MessageAddTileToHand(tileid).pack())
          except:
            print('error here')
  with globalsLock:
    CURRPLAYER = PLAYERTURN.get()
  for num, details in NAMES.items():
    conn, name = details
    conn.sendall(tiles.MessagePlayerTurn(CURRPLAYER).pack())
  with globalsLock:
    PLAYERTURN.put(CURRPLAYER)

  

def client_manager():
  while True:
    global CURRPLAYER, ELIMINATED, LOBBYCLIENTS
    idnum, event = HANDLERQUEUE.get()

    if event == 'Joined':
      # new player NAMES[id][0].sendall(tiles.MessagePlayerJoined(NAMES[idnum][1], idnum).pack())
      
      #every new player joined gets a message from all other players
      for num, details in NAMES.items():
        conn, name = details
        if(num != idnum):
          NAMES[idnum][0].sendall(tiles.MessagePlayerJoined(name, num).pack())
      for num, details in NAMES.items():
        conn, name = details
        if(num != idnum):
          NAMES[num][0].sendall(tiles.MessagePlayerJoined(NAMES[idnum][1], idnum).pack())

      if(len(ACTIVECONNECTIONS) >= 2 and CURRPLAYER == -1): #and there is no game running
        print('ABOUT TO START GAME')
        start_game()

        # print('start a new game')
        # ELIMINATED = 0
        # shufflist = get_random_players()
        # for num, details in NAMES.items():
        #   conn, name = details
        #   count = 0
        #   for item in shufflist:
        #     if(conn == item):
        #       ACTIVELOBBYCONNS.append(num)
        #       LOBBYCLIENTS.append(num)
        #       PLAYERTURN.put(num)
        #   print("playerturn q 1 {}, count {}".format(list(PLAYERTURN.queue), count))
          
        #   CURRPLAYER = PLAYERTURN.get()
        #   print("playerturn q 2 {}, count {}".format(list(PLAYERTURN.queue), count))
        #   PLAYERTURN.put(CURRPLAYER)
        #   conn.sendall(tiles.MessageGameStart().pack())
        #   if(num in ACTIVELOBBYCONNS):
        #     for _ in range(tiles.HAND_SIZE):
        #       tileid = tiles.get_random_tileid()
        #       conn.sendall(tiles.MessageAddTileToHand(tileid).pack())
        #   conn.sendall(tiles.MessagePlayerTurn(CURRPLAYER).pack())

      if(idnum not in ACTIVELOBBYCONNS and CURRPLAYER != -1):
        print('i get in here somehow')
        for num in ACTIVELOBBYCONNS:
          NAMES[idnum][0].sendall(tiles.MessagePlayerTurn(num).pack())
        NAMES[idnum][0].sendall(tiles.MessagePlayerTurn(CURRPLAYER).pack())
        for i in range(0,5):
          for j in range(0,5):
            id, rotation, placerId = board.get_tile(i, j)
            if(id != None and rotation != None and placerId != None):
              NAMES[idnum][0].sendall(tiles.MessagePlaceTile(idnum, id, rotation, i, j).pack())
        for num in ACTIVELOBBYCONNS:
          print('idnum inside bro {} num {}'.format(idnum, num))
          if(board.have_player_position(num)):
            x, y, pos = board.get_player_position(num)
            NAMES[idnum][0].sendall(tiles.MessageMoveToken(num, x, y, pos).pack())
          if num not in LOBBYCLIENTS:
            NAMES[idnum][0].sendall(tiles.MessagePlayerEliminated(num).pack())

      # if no game and len(players) >= 2:
      #   start game
      pass
    elif event == 'Disconected':
      print('idnum of disconnect {}'.format(idnum))
      tempQ = queue.Queue()

      with globalsLock:
        for item in ACTIVELOBBYCONNS:
          if item != idnum:
            tempQ.put(item)
            print('item {}, tempQ {}'.format(item, list(tempQ.queue)))
        ELIMINATED+=1
        print('idnum {}, ALC {}'.format(idnum, ACTIVELOBBYCONNS))
        if idnum in ACTIVELOBBYCONNS:
          ACTIVELOBBYCONNS.remove(idnum)
        conn = NAMES[idnum][0]
        if conn in ACTIVECONNECTIONS:
          ACTIVECONNECTIONS.remove(NAMES[idnum][0])
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
            conn.sendall(tiles.MessagePlayerEliminated(idnum).pack())
        #if there are only two players left then end the game and wipe the board and wait for more clients
        CURRPLAYER = PLAYERTURN.get()
        PLAYERTURN.put(CURRPLAYER)
        print('currplayer {}'.format(CURRPLAYER))
        #that player is now eliminated let everyone know
        #next player turn plz
        
      pass
    elif isinstance(event, tiles.MessagePlaceTile):
      if idnum == CURRPLAYER:
        if board.set_tile(event.x, event.y, event.tileid, event.rotation, event.idnum): 
          # notify client that placement was successful
          for num, details in NAMES.items():
            conn, name = details
            conn.sendall(event.pack())# send to all players so they can see the change

          # check for token movement
          positionupdates, eliminated = board.do_player_movement(ACTIVELOBBYCONNS)

          for event in positionupdates:
            for num, details in NAMES.items():
              conn, name = details
              conn.sendall(event.pack()) # send that to all players
          
          for num1, details1 in NAMES.items(): #LOCKS with globals
            conn1, name1 = details1
            if num1 in eliminated:
              with globalsLock:
                ELIMINATED+=1
              for num, details in NAMES.items():
                conn, name = details
                conn.sendall(tiles.MessagePlayerEliminated(num1).pack())

          # if idnum in eliminated:
          #   ELIMINATED+=1
          #   print('elim {}, alc {}'.format(ELIMINATED, len(ACTIVELOBBYCONNS)))
          #   for num, details in NAMES.items():
          #     conn, name = details
          #     conn.sendall(tiles.MessagePlayerEliminated(idnum).pack()) #send to everyone
          #   #return #need to ignore moves from that player, remove idnum from that list

          # pickup a new tile
          tileid = tiles.get_random_tileid()
          #print("playerturn q OUT {}".format(list(PLAYERTURN.queue)))
          NAMES[idnum][0].sendall(tiles.MessageAddTileToHand(tileid).pack()) #stays the same becuase were only sending it to the player who put a tile down

          # start next turn
          with globalsLock:
            print('end of player turn 1')
            tempNextCurr = PLAYERTURN.get()
            for num, details in NAMES.items():
              conn, name = details
              conn.sendall(tiles.MessagePlayerTurn(tempNextCurr).pack())#pick next idnum, and send to all players. global to hold current player turn
            CURRPLAYER = tempNextCurr
            PLAYERTURN.put(CURRPLAYER)

    elif isinstance(event, tiles.MessageMoveToken):
      if idnum == CURRPLAYER:
        if not board.have_player_position(event.idnum):
            if board.set_player_start_position(event.idnum, event.x, event.y, event.position):
              # check for token movement
              positionupdates, eliminated = board.do_player_movement(ACTIVELOBBYCONNS)

              for event in positionupdates:
                for num, details in NAMES.items():
                  conn, name = details
                  conn.sendall(event.pack()) #send to everyone
              
              for num1, details1 in NAMES.items():
                conn1, name1 = details1
                if num1 in eliminated:
                  with globalsLock:
                    ELIMINATED+=1
                  for num, details in NAMES.items():
                    conn, name = details
                    conn.sendall(tiles.MessagePlayerEliminated(num1).pack())

              # if idnum in eliminated: #SWAP THIS LOOOP AND IF, CHECK IF ALL LOBBY CLIENTS
              #   ELIMINATED+=1
              #   print('elim {}, alc {}'.format(ELIMINATED, len(ACTIVELOBBYCONNS)))
              #   for num, details in NAMES.items():
              #     conn, name = details
              #     conn.sendall(tiles.MessagePlayerEliminated(idnum).pack()) #send to everyone
              #   #return #need to ignore moves from that player, remove idnum from that list
              
              # start next turn
              # if( game has not ended):
              with globalsLock:
                print('end of player turn 2')
                tempNextCurr = PLAYERTURN.get()
                for num, details in NAMES.items():
                  conn, name = details
                  conn.sendall(tiles.MessagePlayerTurn(tempNextCurr).pack())#pick next idnum, and send to all players. global to hold current player turn
                CURRPLAYER = tempNextCurr
                PLAYERTURN.put(CURRPLAYER)

    print('got to here?')
    print('elims {}, alcs {}'.format(ELIMINATED, len(ACTIVELOBBYCONNS)))
    if(ELIMINATED == (len(ACTIVELOBBYCONNS) - 1)):
      #change current player to null etc
      # start end game process
      print('game is over')
      print('handlerq {}'.format(list(HANDLERQUEUE.queue)))
      with globalsLock:
        CURRPLAYER = -1
        ELIMINATED = -2
        ACTIVELOBBYCONNS.clear()
        LOBBYCLIENTS.clear()
        print('playerturn res 1 {}'.format(list(PLAYERTURN.queue)))
        with PLAYERTURN.mutex:
          PLAYERTURN.queue.clear()
        print('playerturn res 2 {}'.format(list(PLAYERTURN.queue)))

        board.reset()

      print('len AC {}'.format(len(ACTIVECONNECTIONS)))
      if(len(ACTIVECONNECTIONS)>=2 and CURRPLAYER == -1):
        print('got to another game!')
        start_game()

      #check if more than4 players, then start game
      # continue

    HANDLERQUEUE.task_done() 
     
      
def client_handler(connection, address):
  host, port = address
  name = '{}:{}'.format(host, port)
  
  with mylock:
    idnum = threading.get_ident()
    NAMES[idnum] = [connection, name]
    ACTIVECONNECTIONS.append(connection)
    # LOBBYCLIENTS.append(idnum) #the current players in the current game
    # live_idnums = LOBBYCLIENTS
    #ACTIVELOBBYCONNS.append((connection,idnum))
  #NAMES.append(name)
  #ditcionary mapping id to name

  print("[ACTIVE CONNECTIONS] {}",format(len(ACTIVECONNECTIONS)))

  print('[IDNUM] ',format(idnum))
  #LOBBYCLIENTS.append(idnum) #the current players in the current game
  #give new connection a new idnum
  #live_idnums=LOBBYCLIENTS
  #print('[LOBBYCLIENTS] {} [live_idnums] {}'.format(LOBBYCLIENTS, live_idnums))
  
  #ACTIVELOBBYCONNS.append((connection, idnum)) #add if they are apart of the game
  #print('[ACTIVELOBBYCONNS len] {}',format((ACTIVELOBBYCONNS)))

  connection.sendall(tiles.MessageWelcome(idnum).pack())
  #connection.sendall(tiles.MessagePlayerJoined(name, idnum).pack())

  with globalsLock:
    HANDLERQUEUE.put((idnum, 'Joined'))

  buffer = bytearray()

  while True: #and if its this clients turn
    #print('in first while')
    # if(CURRPLAYER != idnum):
    #   chonk = connection.recv(4096)
    #   if not chonk:
    #     print('got to insdie chonk1 {}'.format(chonk))
    #     with mylock:
    #       print('conn 1 {} ac 1 {}'.format(connection, ACTIVECONNECTIONS))
    #       if(connection in ACTIVECONNECTIONS):
    #         HANDLERQUEUE.put((idnum, 'Disconected'))
    #         return

    # if(CURRPLAYER != -1):
      #print('game has started, idnum {}'.format(idnum))
      # if(CURRPLAYER != idnum):
        # chonk = connection.recv(4096)
        # if not chonk:
        #   print('got to insdie chonk2 {}'.format(chonk))
        #   with mylock:
        #     print('conn 2 {} ac 2 {}'.format(connection, ACTIVECONNECTIONS))
        #     if(connection in ACTIVECONNECTIONS):
        #       HANDLERQUEUE.put((idnum, 'Disconected'))
        #       return
      # if(CURRPLAYER == idnum):
        
        print('id is curr player, id {}'.format(idnum))
        try:
          chunk = connection.recv(4096)
          print('chunk {}'.format(chunk))
          with mylock:
            if not chunk:
              print('client {} disconnected'.format(address))
              if(connection in ACTIVECONNECTIONS):
                HANDLERQUEUE.put((idnum, 'Disconected'))
                return
            # return #change current player turn, remove this idnum from list

        except:
          pass

        buffer.extend(chunk)
        if(CURRPLAYER != -1):
          if(CURRPLAYER == idnum):
            while True:
              msg, consumed = tiles.read_message_from_bytearray(buffer)
              if not consumed:
                break

              buffer = buffer[consumed:]

              print('received message {}'.format(msg))

              with globalsLock:
                HANDLERQUEUE.put((idnum, msg))
              
              print('in second while')
  

      

def start():
  # create a TCP/IP socket
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

  # listen on all network interfaces
  server_address = ('', 30020) 
  sock.bind(server_address)

  print('listening on {}'.format(sock.getsockname()))

  sock.listen(5)

  managerThread = threading.Thread(target=client_manager)
  managerThread.start()

  while True:
    # handle each new connection independently
    connection, client_address = sock.accept()
    print('received connection from {}'.format(client_address))
    thread = threading.Thread(target=client_handler, args=(connection, client_address))
    thread.start()

    # ACTIVECONNECTIONS.append(connection)
    # print("[ACTIVE CONNECTIONS] {}",format(len(ACTIVECONNECTIONS)))

    #do in manager
    # if (len(ACTIVECONNECTIONS) > 1):
    #   if (len(ACTIVECONNECTIONS) > 2):
    #     pass  
    #   get_random_players()
    #   print('we have 2 connections'):



print("[STARTING] server is starting...")
start()