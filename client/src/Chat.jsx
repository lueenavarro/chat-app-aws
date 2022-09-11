import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';

const URL = 'wss://3bgt0lfzhi.execute-api.ap-southeast-1.amazonaws.com/prod';

const Chat = () => {
  const [searchParams] = useSearchParams();
  const [socket, setSocket] = useState();
  const [room, setRoom] = useState();
  const [user, setUser] = useState();
  const [currentMessage, setCurrentMessage] = useState('');
  const [events, setEvents] = useState([]);

  const handleMessage = (e, currentUser) => {
    const body = JSON.parse(e.data);
    const actions = {
      enter: () =>
        setEvents((prevEvents) =>
          prevEvents.concat(
            <span className='status'>{body.username} entered!</span>
          )
        ),
      leave: () =>
        setEvents((prevEvents) =>
          prevEvents.concat(
            <span className='status'>{body.username} left!</span>
          )
        ),
      message: () =>
        setEvents((prevEvents) =>
          prevEvents.concat(
            <div
              className='chat'
              style={{
                justifySelf: body.username === currentUser ? 'right' : 'left',
                backgroundColor:
                  body.username === currentUser ? 'lightgray' : 'white',
              }}
            >
              <span className='from'>{body.username}</span>
              {body.message}
            </div>
          )
        ),
    };

    if (typeof actions[body.action] === 'function') actions[body.action]();
  };

  // parse username and room id
  useEffect(() => {
    const currentRoomId = searchParams.get('room');
    const currentUser = searchParams.get('username');

    if (!currentRoomId || !currentUser) return;

    setRoom(currentRoomId);
    setUser(currentUser);
    const websocket = new WebSocket(URL);
    websocket.addEventListener('open', () => {
      console.log('Connection opened!');
      setSocket(websocket);
      websocket.send(
        JSON.stringify({
          action: 'enter',
          room_id: currentRoomId,
          username: currentUser,
        })
      );
    });
    websocket.addEventListener('error', (e) =>
      console.log('Connection error!', e)
    );
    websocket.addEventListener('closed', () =>
      console.log('Connection closed!')
    );
    websocket.addEventListener('message', (e) => handleMessage(e, currentUser));
    return () => websocket.close();
  }, [searchParams]);

  if (!socket) return 'Connecting...';
  if (!room) return 'Invalid Room Id';
  if (!user) return 'Invalid username';

  return (
    <>
      <div className='room'>Room: {room}</div>
      <div className='chats'>
        {events.map((event, index) => (
          <div key={index} className='event'>
            {event}
          </div>
        ))}
      </div>
      <form
        className='send'
        onSubmit={(e) => {
          e.preventDefault();
          if (!currentMessage) return;
          socket.send(
            JSON.stringify({
              action: 'sendmessage',
              message: currentMessage,
              from: user,
            })
          );
          setCurrentMessage('');
        }}
      >
        <input
          type='text'
          value={currentMessage}
          onChange={(e) => setCurrentMessage(e.target.value)}
          autoFocus
        />
        <button>SEND</button>
      </form>
    </>
  );
};

export default Chat;
