import socket 
import sys
import tiles
import threading

board = tiles.Board()
ACTIVECONNECTIONS = []
LOBBYCLIENTS = [] 

def client_handler(connection, address):
  host, port = address
  name = '{}:{}'.format(host, port)

  idnum = threading.get_ident()
  print('[IDNUM] ',format(idnum))
  LOBBYCLIENTS.append(idnum) #the current players in the current game
  #give new connection a new idnum
  live_idnums=LOBBYCLIENTS
  print('[LOBBYCLIENTS] {} [live_idnums] {}'.format(LOBBYCLIENTS, live_idnums))

  connection.send(tiles.MessageWelcome(idnum).pack())
  for i in range(len(LOBBYCLIENTS)):
    connection.send(tiles.MessagePlayerJoined(name, LOBBYCLIENTS[i]).pack()) #need to send to all, need a global list to send to new players, the old players already in lobby
    #if there are more than 2 players and up to 4 players in the lobby then start
    connection.send(tiles.MessageGameStart().pack()) #send to everyone for new game start (dont start until we have atleast two clients)

  #do for every player (not connection, since may be mroe connections), fill tiles
  for i in range(len(LOBBYCLIENTS)):
    for _ in range(tiles.HAND_SIZE):
      tileid = tiles.get_random_tileid()
      connection.send(tiles.MessageAddTileToHand(tileid).pack())
    
    connection.send(tiles.MessagePlayerTurn(LOBBYCLIENTS[i]).pack()) #send message to everyone, for that players turn
  
  #board = tiles.Board() #make this global

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
      # sent by the player to put a tile onto the board (in all turns except
      # their second)
      if isinstance(msg, tiles.MessagePlaceTile): #checking if tile is in their hand, ignore the move
        if board.set_tile(msg.x, msg.y, msg.tileid, msg.rotation, msg.idnum): 
          # notify client that placement was successful
          
          for i in ACTIVECONNECTIONS:
            print("AC: {}".format(i))
            i.send(msg.pack())# send to all players so they can see the change

          # check for token movement
          positionupdates, eliminated = board.do_player_movement(live_idnums)

          for msg in positionupdates:
            for i in ACTIVECONNECTIONS:
              print("AC: {}".format(i))
              i.send(msg.pack())
            #connection.send(msg.pack()) # send that to all players
          
          if idnum in eliminated:
            connection.send(tiles.MessagePlayerEliminated(idnum).pack()) #send to everyone
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

  while True:
    # handle each new connection independently
    connection, client_address = sock.accept()
    print('received connection from {}'.format(client_address))
    thread = threading.Thread(target=client_handler, args=(connection, client_address))
    thread.start()
    ACTIVECONNECTIONS.append(connection)
    print("[ACTIVE CONNECTIONS] {}",format(threading.activeCount()-1))

print("[STARTING] server is starting...")
start()

#time.sleep(3)
    # print("[Active Connections]: {}".format(len(CONNECTIONS)))
    # if (len(CONNECTIONS) > 1):
    #   #time.sleep(2)
    #   CONNECTIONS[0].send(tiles.MessageGameStart().pack()) #send to everyone for new game start (dont start until we have atleast two clients)
    #   if(HANDLERQUEUE.not_empty):
    #     #time.sleep(3)
    #     #print("[ACTIVE CONNECTIONS CM] {}".format(len(CONNECTIONS)))
    #     for conn in CONNECTIONS:
    #       items = HANDLERQUEUE.get()
    #       print("[ITEMS]: {}".format(items))
    #       func = items[0]
    #       args = items[1:]
    #       print("[Func]: {}, [Args]: {}".format(func, args))
    #       #func(*args)
    #       conn.send(*args)