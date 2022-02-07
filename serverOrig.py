# CITS3002 2021 Assignment
#
# This file implements a basic server that allows a single client to play a
# single game with no other participants, and very little error checking.
#
# Any other clients that connect during this time will need to wait for the
# first client's game to complete.
#
# Your task will be to write a new server that adds all connected clients into
# a pool of players. When enough players are available (two or more), the server
# will create a game with a random sample of those players (no more than
# tiles.PLAYER_LIMIT players will be in any one game). Players will take turns
# in an order determined by the server, continuing until the game is finished
# (there are less than two players remaining). When the game is finished, if
# there are enough players available the server will start a new game with a
# new selection of clients.

import socket
import sys
import tiles

from _thread import *
import threading

import queue

ThreadCount = 0
board = tiles.Board()

eventQ = queue.Queue()

#need global ist of players to pick from
#global list of all connections 


def manager():
  pass
  # while True:
  #   idnum, event = eventQ.get()

  #   if event == 'Joined':
  #     # new player
  #     if no game and len(players) >= 2:
  #       start game
  #     pass
  #   elif event == 'Disconected':
  #     pass
  #   elif isinstance(event, tiles.MessagePlaceTile):
  #     if idnum == cur
  #   elif isinstance(xx)

    
def client_handler(connection, address):
  host, port = address
  name = '{}:{}'.format(host, port)

  idnum = 0
  live_idnums = [idnum] #the current players in the current game
  #give new connection a new idnum

  connection.send(tiles.MessageWelcome(idnum).pack())
  #wait until i have connections
  connection.send(tiles.MessagePlayerJoined(name, idnum).pack()) #need to send to all, need a global list to send to new players, the old players already in lobby
  # connection.send(tiles.MessageGameStart().pack()) #send to everyone for new game start (dont start until we have atleast two clients)

  #do for every player (not connection, since may be mroe connections), fill tiles
  # for _ in range(tiles.HAND_SIZE):
  #   tileid = tiles.get_random_tileid()
  #   connection.send(tiles.MessageAddTileToHand(tileid).pack())
  # 
  # connection.send(tiles.MessagePlayerTurn(idnum).pack()) #send message to everyone, for that players turn
  
  # board = tiles.Board() #make this global

  eventQ.put((idnum, 'Joined'))

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
        eventQ.put((idnum, 'Disconnected'))
        break

      buffer = buffer[consumed:]

      print('received message {}'.format(msg))

      eventQ.put((idnum, msg))

      # sent by the player to put a tile onto the board (in all turns except
      # their second)
      if isinstance(msg, tiles.MessagePlaceTile): #checking if tile is in their hand, ignore the move
        if board.set_tile(msg.x, msg.y, msg.tileid, msg.rotation, msg.idnum): 
          # notify client that placement was successful
          connection.send(msg.pack())# send to all players so they can see the change

          # check for token movement
          positionupdates, eliminated = board.do_player_movement(live_idnums)

          for msg in positionupdates:
            connection.send(msg.pack()) # send that to all players
          
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
              connection.send(msg.pack()) #send to everyone
            
            if idnum in eliminated:
              connection.send(tiles.MessagePlayerEliminated(idnum).pack()) #send to everyone
              return #same as 84
            
            # start next turn
            connection.send(tiles.MessagePlayerTurn(idnum).pack()) #pick next idnum and send to all players


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
  client_handler(connection, client_address)
  # start_new_thread(client_handler,(connection, client_address))
  # ThreadCount+=1
  # print("ThreadCount: {}".format(ThreadCount) )