if event == 'Joined':
      # new player NAMES[id][0].sendall(tiles.MessagePlayerJoined(NAMES[idnum][1], idnum).pack())
      
      for num, details in NAMES.items():
        conn, name = details
        NAMES[idnum][0].sendall(tiles.MessagePlayerJoined(name, num).pack())
      for num, details in NAMES.items():
        conn, name = details
        if(num != idnum):
          NAMES[num][0].sendall(tiles.MessagePlayerJoined(NAMES[idnum][1], idnum).pack())

      if(len(ACTIVECONNECTIONS) == 3):
        print('got 3')
        
      if( len(ACTIVECONNECTIONS) == 4): #and there is no game running atm
        #start game
        pass
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
        # print('ALC {}'.format(ACTIVELOBBYCONNS))
        # print('CURRPLAYER {}'.format(CURRPLAYER))

        # print('NAMES {}'.format(CURRPLAYER))
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
            if num in eliminated:
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
                # if(num in ACTIVELOBBYCONNS):
                if num in eliminated:
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
    HANDLERQUEUE.task_done() 