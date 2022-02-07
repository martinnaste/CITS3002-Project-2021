import socket 
import sys
import tiles
import threading
import time
import queue
import random

board = tiles.Board()
ACTIVECONNECTIONS = []
LOBBYCLIENTS = [] 
ACTIVELOBBYCONNS = []

GAMELOBBYID = []
GAMELOBBYCONN = []

HANDLERQUEUE = queue.Queue()
PLAYERTURN = queue.Queue()
CURRPLAYER = -1

def get_random_players():
  #get the frist up to four in active connections into temp array
  #remove 1st and add to end, up to 4 times
  #shuffle temp array, then put each item in by that shuffled order into player queue
  number = 0
  if (len(ACTIVELOBBYCONNS) > 1):
    number = 2
    print('we have 2 connections')
    if (len(ACTIVELOBBYCONNS) > 2):
      number = 3
      print('we have 3 connections')
      if (len(ACTIVELOBBYCONNS) > 3):
        number = 4  
        print('we have 4 connections')  
  
  print('[number] {}'.format(number))
  TempList = []
  for i in range(number-1):
    print('[i] {} [TEMPLIST] {}'.format(i, TempList))
    TempList.append(ACTIVECONNECTIONS[0])
    ACTIVECONNECTIONS.pop(0)
    ACTIVECONNECTIONS.append(TempList[i])
  random.shuffle(TempList)
  return TempList

  # if (len(ACTIVECONNECTIONS) > 1):
  #     print("2 players")
  #     GAMELOBBYID.append(LOBBYCLIENTS[0])
  #     GAMELOBBYCONN.append(ACTIVECONNECTIONS[0])
  #     GAMELOBBYID.append(LOBBYCLIENTS[1])
  #     GAMELOBBYCONN.append(ACTIVECONNECTIONS[1])
  #     print("[GAMELOBBYID] 0: {}".format(GAMELOBBYID[0]))
  #     print("[GAMELOBBYID] 1: {}".format(GAMELOBBYID[1]))
  #     if (len(ACTIVECONNECTIONS) > 2):
  #       print("more than 2 players")
  #       GAMELOBBYID.append(LOBBYCLIENTS[2])
  #       GAMELOBBYCONN.append(ACTIVECONNECTIONS[0])
  #       GAMELOBBYID.append(LOBBYCLIENTS[3])
  #       GAMELOBBYCONN.append(ACTIVECONNECTIONS[0])
  #       print("[GAMELOBBYID] 2: {}".format(GAMELOBBYID[2]))
  #       print("[GAMELOBBYID] 3: {}".format(GAMELOBBYID[3]))
  #     random.shuffle(GAMELOBBYID)
  #     print("[GAMELOBBYID]: {}".format(GAMELOBBYID))
      
  #     for item in GAMELOBBYID:
  #       PLAYERTURN.put(item)
  #     CURRPLAYER = PLAYERTURN.get()
  #     print('[CURRENTPLAYER in main] {}'.format(CURRPLAYER))
  #     PLAYERTURN.put(CURRPLAYER)
  #     connection.send(tiles.MessageGameStart().pack())

def client_manager():
  pass
  # while True:
    
  #   if(len(ACTIVECONNECTIONS) > 1):
  #     print('Len AC {}'.format(len(ACTIVECONNECTIONS)))
  #     tempList = get_random_players()
  #     time.sleep(3)
  #     print('[TEMPLIST] {}'.format(tempList))
  #     CURRPLAYER = tempList[0]
      


def client_handler(connection, address):
  host, port = address
  name = '{}:{}'.format(host, port)

  ACTIVECONNECTIONS.append(connection)
  print("[ACTIVE CONNECTIONS] {}",format(len(ACTIVECONNECTIONS)))

  idnum = threading.get_ident()
  print('[IDNUM] ',format(idnum))
  LOBBYCLIENTS.append(idnum) #the current players in the current game
  #give new connection a new idnum
  live_idnums=LOBBYCLIENTS
  print('[LOBBYCLIENTS] {} [live_idnums] {}'.format(LOBBYCLIENTS, live_idnums))
  
  ACTIVELOBBYCONNS.append((connection, idnum))
  #print('[ACTIVELOBBYCONNS len] {}',format((ACTIVELOBBYCONNS)))

  connection.sendall(tiles.MessageWelcome(idnum).pack())
  for conn in ACTIVELOBBYCONNS:
    print('[CONN 1 ] {} [CONN 2 ] {}'.format(conn[0], conn[1]))
    conn[0].sendall(tiles.MessagePlayerJoined(name, idnum).pack())



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





import socket 
import sys
import tiles
import threading
import time
import queue
import random

board = tiles.Board()
ACTIVECONNECTIONS = []
LOBBYCLIENTS = []
NAMES = {}
ACTIVELOBBYCONNS = [] 

GAMELOBBYID = []
GAMELOBBYCONN = []

HANDLERQUEUE = queue.Queue()
PLAYERTURN = queue.Queue()
CURRPLAYER = -1

mylock = threading.Lock() #lock for each group of things i am assigning

def get_random_players():
  #get the frist up to four in active connections into temp array
  #remove 1st and add to end, up to 4 times
  #shuffle temp array, then put each item in by that shuffled order into player queue
  number = 0
  if (len(ACTIVELOBBYCONNS) > 1):
    number = 2
    print('we have 2 connections')
    if (len(ACTIVELOBBYCONNS) > 2):
      number = 3
      print('we have 3 connections')
      if (len(ACTIVELOBBYCONNS) > 3):
        number = 4  
        print('we have 4 connections')  
  
  print('[number] {}'.format(number))
  TempList = []
  for i in range(number-1):
    print('[i] {} [TEMPLIST] {}'.format(i, TempList))
    TempList.append(ACTIVECONNECTIONS[0])
    ACTIVECONNECTIONS.pop(0)
    ACTIVECONNECTIONS.append(TempList[i])
  random.shuffle(TempList)
  return TempList

  # if (len(ACTIVECONNECTIONS) > 1):
  #     print("2 players")
  #     GAMELOBBYID.append(LOBBYCLIENTS[0])
  #     GAMELOBBYCONN.append(ACTIVECONNECTIONS[0])
  #     GAMELOBBYID.append(LOBBYCLIENTS[1])
  #     GAMELOBBYCONN.append(ACTIVECONNECTIONS[1])
  #     print("[GAMELOBBYID] 0: {}".format(GAMELOBBYID[0]))
  #     print("[GAMELOBBYID] 1: {}".format(GAMELOBBYID[1]))
  #     if (len(ACTIVECONNECTIONS) > 2):
  #       print("more than 2 players")
  #       GAMELOBBYID.append(LOBBYCLIENTS[2])
  #       GAMELOBBYCONN.append(ACTIVECONNECTIONS[0])
  #       GAMELOBBYID.append(LOBBYCLIENTS[3])
  #       GAMELOBBYCONN.append(ACTIVECONNECTIONS[0])
  #       print("[GAMELOBBYID] 2: {}".format(GAMELOBBYID[2]))
  #       print("[GAMELOBBYID] 3: {}".format(GAMELOBBYID[3]))
  #     random.shuffle(GAMELOBBYID)
  #     print("[GAMELOBBYID]: {}".format(GAMELOBBYID))
      
  #     for item in GAMELOBBYID:
  #       PLAYERTURN.put(item)
  #     CURRPLAYER = PLAYERTURN.get()
  #     print('[CURRENTPLAYER in main] {}'.format(CURRPLAYER))
  #     PLAYERTURN.put(CURRPLAYER)
  #     connection.send(tiles.MessageGameStart().pack())

def client_manager():
  pass
      
def client_handler(connection, address):
  host, port = address
  name = '{}:{}'.format(host, port)
  
  with mylock:
    idnum = threading.get_ident()
    NAMES[idnum] = [connection, name]
    ACTIVECONNECTIONS.append(connection)
  #NAMES.append(name)
  #ditcionary mapping id to name

  ACTIVECONNECTIONS.append(connection)
  print("[ACTIVE CONNECTIONS] {}",format(len(ACTIVECONNECTIONS)))

  idnum = threading.get_ident()
  print('[IDNUM] ',format(idnum))
  LOBBYCLIENTS.append(idnum) #the current players in the current game
  #give new connection a new idnum
  live_idnums=LOBBYCLIENTS
  print('[LOBBYCLIENTS] {} [live_idnums] {}'.format(LOBBYCLIENTS, live_idnums))
  
  ACTIVELOBBYCONNS.append((connection, idnum))
  #print('[ACTIVELOBBYCONNS len] {}',format((ACTIVELOBBYCONNS)))

  connection.sendall(tiles.MessageWelcome(idnum).pack())
  for conn in ACTIVELOBBYCONNS:
    print('[CONN 1 ] {} [CONN 2 ] {}'.format(conn[0], conn[1]))
    conn[0].sendall(tiles.MessagePlayerJoined(name, idnum).pack())

  buffer = bytearray()
  print("outisde while")
  while True:
    print("inside while")

    print("outsite if")
    if(len(ACTIVELOBBYCONNS) > 1 and idnum == firstplayer):
      print("inside if")
      for conn in ACTIVELOBBYCONNS:
        conn[0].send(tiles.MessageGameStart().pack())
        for _ in range(tiles.HAND_SIZE):
          tileid = tiles.get_random_tileid()
          conn[0].send(tiles.MessageAddTileToHand(tileid).pack())
      connection.send(tiles.MessagePlayerTurn(idnum).pack())
    
    chunk = connection.recv(4096)
    if not chunk:
      print('client {} disconnected'.format(address))
      return #change current player turn, remove this idnum from list

    buffer.extend(chunk)

    while True:
      msg, consumed = tiles.read_message_from_bytearray(buffer)
      if not consumed:
        break

      buffer = buffer[consumed:]

      print('received message {}'.format(msg))
      # sent by the player to put a tile onto the board (in all turns except
      # their second)
      if isinstance(msg, tiles.MessagePlaceTile): #checking if tile is in their hand, ignore the move
        if board.set_tile(msg.x, msg.y, msg.tileid, msg.rotation, msg.idnum): 
          # notify client that placement was successful
          
          for conn in ACTIVELOBBYCONNS:
            print("AC: {}".format(conn))
            conn[0].send(msg.pack())# send to all players so they can see the change

          # check for token movement
          positionupdates, eliminated = board.do_player_movement(live_idnums)

          for msg in positionupdates:
            for conn in ACTIVELOBBYCONNS:
              print("AC: {}".format(i))
              conn[0].send(msg.pack())
            #connection.send(msg.pack()) # send that to all players
          
          if idnum in eliminated:
            for conn in ACTIVELOBBYCONNS:
              conn[0].send(tiles.MessagePlayerEliminated(idnum).pack()) #send to everyone
              live_idnums.remove(idnum)
              LOBBYCLIENTS = live_idnums
              return #need to ignore moves from that player, remove idnum from that list

          # pickup a new tile
          tileid = tiles.get_random_tileid()
          connection.send(tiles.MessageAddTileToHand(tileid).pack()) #stays the same becuase were only sending it to the player who put a tile down

          # start next turn
          connection.send(tiles.MessagePlayerTurn(idnum).pack())#pick next idnum, and send to all players. global to hold current player turn

      # sent by the player in the second turn, to choose their token's
      # starting path
      elif isinstance(msg, tiles.MessageMoveToken):
        if not board.have_player_position(msg.idnum):
          if board.set_player_start_position(msg.idnum, msg.x, msg.y, msg.position):
            # check for token movement
            positionupdates, eliminated = board.do_player_movement(live_idnums)

            for msg in positionupdates:
              for i in ACTIVECONNECTIONS:
                print("AC: {}".format(i))
                i.send(msg.pack())
              # connection.send(msg.pack()) #send to everyone
            
            if idnum in eliminated:
              connection.send(tiles.MessagePlayerEliminated(idnum).pack()) #send to everyone
              return #same as 84
            
            # start next turn
            connection.send(tiles.MessagePlayerTurn(idnum).pack()) #pick next idnum and send to all players




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



#NAMES[idnum][0].sendall(tiles.MessagePlayerJoined(NAMES[idnum][1], idnum).pack())
      for num, details in NAMES.items():
        conn, name = details
        NAMES[idnum][0].sendall(tiles.MessagePlayerJoined(name, num).pack())
      for num, details in NAMES.items():
        conn, name = details
        if(num != idnum):
          print("true_, num {}".format(num))
          #   continue
          # print('NAMES at num {}, id {}'.format(NAMES[num], num))
          # print('NAMES num[0] {}'.format(NAMES[num][0]))
          # print('NAMES num[1] {}'.format(NAMES[num][1]))
          NAMES[num][0].sendall(tiles.MessagePlayerJoined(NAMES[idnum][1], idnum).pack())
          # for conn in ACTIVECONNECTIONS:
          #   if(NAMES[idnum][0] != conn):
          #     NAMES[idnum][0].sendall(tiles.MessagePlayerJoined(NAMES[num][1], id).pack())  

      # if no game and len(players) >= 2:
      #   start game
      pass
    elif event == 'Disconected':
      pass
    # elif isinstance(event, tiles.MessagePlaceTile):
    #   if idnum == currentplayer
    # elif isinstance(xx)
      
def client_handler(connection, address):
  host, port = address
  name = '{}:{}'.format(host, port)
  
  with mylock:
    idnum = threading.get_ident()
    NAMES[idnum] = [connection, name]
    ACTIVECONNECTIONS.append(connection)
    LOBBYCLIENTS.append(idnum) #the current players in the current game
    live_idnums = LOBBYCLIENTS
    #ACTIVELOBBYCONNS.append((connection,idnum))
  #NAMES.append(name)
  #ditcionary mapping id to name

  print("[ACTIVE CONNECTIONS] {}",format(len(ACTIVECONNECTIONS)))

  print('[IDNUM] ',format(idnum))
  #LOBBYCLIENTS.append(idnum) #the current players in the current game
  #give new connection a new idnum
  #live_idnums=LOBBYCLIENTS
  print('[LOBBYCLIENTS] {} [live_idnums] {}'.format(LOBBYCLIENTS, live_idnums))
  
  #ACTIVELOBBYCONNS.append((connection, idnum)) #add if they are apart of the game
  #print('[ACTIVELOBBYCONNS len] {}',format((ACTIVELOBBYCONNS)))

  connection.sendall(tiles.MessageWelcome(idnum).pack())
  #connection.sendall(tiles.MessagePlayerJoined(name, idnum).pack())

  HANDLERQUEUE.put((idnum, 'Joined'))

  buffer = bytearray()

  while True:
    
    chunk = connection.recv(4096)
    if not chunk:
      print('client {} disconnected'.format(address))
      return #change current player turn, remove this idnum from list

    buffer.extend(chunk)

    while True:
      msg, consumed = tiles.read_message_from_bytearray(buffer)
      if not consumed:
        break

      buffer = buffer[consumed:]

      print('received message {}'.format(msg))

      HANDLERQUEUE.put((idnum, msg))




################################### 12/5
import socket 
import sys
import tiles
import threading
import time
import queue
import random

board = tiles.Board()
ACTIVECONNECTIONS = []
LOBBYCLIENTS = []

WAITINGLOBBY = []

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
  
  #print('[number] {}'.format(number))
  #print('[ACTIVECONNECTIONS] {}'.format(ACTIVECONNECTIONS))
  TempList = []
  for i in range(number):
    #print('[i] {} [TEMPLIST] {}'.format(i, TempList))
    #print('[ACTIVECONNECTIONS] {}'.format(ACTIVECONNECTIONS[0]))
    TempList.append(ACTIVECONNECTIONS[0])
    ACTIVECONNECTIONS.pop(0)
    ACTIVECONNECTIONS.append(TempList[i])
    #print('[TEMPLIST] {}'.format(TempList))
  random.shuffle(TempList)
  print('[TEMPLIST shuffle] {}'.format(TempList))

  return TempList

def client_manager():
  while True:
    global CURRPLAYER, ELIMINATED, LOBBYCLIENTS
    idnum, event = HANDLERQUEUE.get()

    if event == 'Joined':
      # new player NAMES[id][0].sendall(tiles.MessagePlayerJoined(NAMES[idnum][1], idnum).pack())
      
      for num, details in NAMES.items():
        conn, name = details
        if(num != idnum):
          NAMES[idnum][0].sendall(tiles.MessagePlayerJoined(name, num).pack())
      for num, details in NAMES.items():
        conn, name = details
        if(num != idnum):
          NAMES[num][0].sendall(tiles.MessagePlayerJoined(NAMES[idnum][1], idnum).pack())

      if(len(ACTIVECONNECTIONS) >= 2 and CURRPLAYER == -1): #and there is no game running
        print('start a new game')
        ELIMINATED = 0
        shufflist = get_random_players()
        for num, details in NAMES.items():
          conn, name = details
          count = 0
          for item in shufflist:
            if(conn == item):
              ACTIVELOBBYCONNS.append(num)
              LOBBYCLIENTS.append(num)
              PLAYERTURN.put(num)
          print("playerturn q 1 {}, count {}".format(list(PLAYERTURN.queue), count))
          
          CURRPLAYER = PLAYERTURN.get()
          print("playerturn q 2 {}, count {}".format(list(PLAYERTURN.queue), count))
          PLAYERTURN.put(CURRPLAYER)
          conn.sendall(tiles.MessageGameStart().pack())
          if(num in ACTIVELOBBYCONNS):
            for _ in range(tiles.HAND_SIZE):
              tileid = tiles.get_random_tileid()
              conn.sendall(tiles.MessageAddTileToHand(tileid).pack())
          conn.sendall(tiles.MessagePlayerTurn(CURRPLAYER).pack())

      if(NAMES[idnum][0] not in ACTIVELOBBYCONNS and CURRPLAYER != -1):
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
          
          for num, details in NAMES.items():
            conn, name = details
            # if(num in ACTIVELOBBYCONNS):
            if num in eliminated and conn in ACTIVECONNECTIONS:
              ELIMINATED+=1
              conn.sendall(tiles.MessagePlayerEliminated(num).pack())
              NAMES[idnum][0].sendall(tiles.MessagePlayerEliminated(num).pack())
          
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
              
              
              for num, details in NAMES.items():
                conn, name = details
                if num in eliminated and conn in ACTIVECONNECTIONS:
                  ELIMINATED+=1
                  conn.sendall(tiles.MessagePlayerEliminated(num).pack())
                  NAMES[idnum][0].sendall(tiles.MessagePlayerEliminated(num).pack())

              # if idnum in eliminated: #SWAP THIS LOOOP AND IF, CHECK IF ALL LOBBY CLIENTS
              #   ELIMINATED+=1
              #   print('elim {}, alc {}'.format(ELIMINATED, len(ACTIVELOBBYCONNS)))
              #   for num, details in NAMES.items():
              #     conn, name = details
              #     conn.sendall(tiles.MessagePlayerEliminated(idnum).pack()) #send to everyone
              #   #return #need to ignore moves from that player, remove idnum from that list
              
              # start next turn
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
      CURRPLAYER = -1
      ELIMINATED = -2
      ACTIVELOBBYCONNS.clear()

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

  HANDLERQUEUE.put((idnum, 'Joined'))

  buffer = bytearray()

  while True: #and if its this clients turn
    #print('in first while')
    if(CURRPLAYER != -1):
      #print('game has started, idnum {}'.format(idnum))
      if(CURRPLAYER == idnum):
        
        print('id is curr player, id {}'.format(idnum))
        chunk = connection.recv(4096)
        if not chunk:
          print('client {} disconnected'.format(address))
          # return #change current player turn, remove this idnum from list

        buffer.extend(chunk)

        
        while True:
          msg, consumed = tiles.read_message_from_bytearray(buffer)
          if not consumed:
            break

          buffer = buffer[consumed:]

          print('received message {}'.format(msg))

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

############################### 13/5 disconnect
tempQ = queue.Queue()
      with globalsLock:
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
        CURRPLAYER = PLAYERTURN.get()
        PLAYERTURN.put(CURRPLAYER)
        #that player is now eliminated let everyone know
        #next player turn plz