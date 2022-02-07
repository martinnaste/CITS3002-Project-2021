def start_game():
  global CURRPLAYER, ELIMINATED, LOBBYCLIENTS
  print('start a new game')
  with globalsLock:
    ELIMINATED = 0
  shufflist = get_random_players()
  print('shuflist {}'.format(shufflist))
  for num, details in NAMES.items():
    conn, name = details
    count = 0
    for item in shufflist:
      if(conn == item):
        count+=1
        with globalsLock:
          ACTIVELOBBYCONNS.append(num)
          LOBBYCLIENTS.append(num)
          PLAYERTURN.put(num)
    print("playerturn q 1 {}, count {}".format(list(PLAYERTURN.queue), count))
    
    with globalsLock:
      CURRPLAYER = PLAYERTURN.get()
      print('curr player {}'.format(CURRPLAYER))
      print("playerturn q 2 {}, count {}".format(list(PLAYERTURN.queue), count))
      PLAYERTURN.put(CURRPLAYER)
    
    print('conn b4 start {}, currpl {}'.format(conn, CURRPLAYER))
    conn.sendall(tiles.MessageGameStart().pack())
    if(num in ACTIVELOBBYCONNS):
      for _ in range(tiles.HAND_SIZE):
        tileid = tiles.get_random_tileid()
        conn.sendall(tiles.MessageAddTileToHand(tileid).pack())
    conn.sendall(tiles.MessagePlayerTurn(CURRPLAYER).pack())