import { useState } from 'react';
import { createSearchParams, useNavigate } from 'react-router-dom';

const Home = () => {
  const navigate = useNavigate();
  const [room, setRoom] = useState('');
  const [user, setUser] = useState('');

  return (
    <div className='home-container'>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          navigate({
            pathname: '/chat',
            search: createSearchParams({
              room: room,
              username: user,
            }).toString(),
          });
        }}
      >
        <input
          type='text'
          placeholder='Room'
          value={room}
          onChange={(e) => setRoom(e.target.value.toLowerCase())}
          autoFocus
        />
        <br />
        <input
          type='text'
          placeholder='Username'
          value={user}
          onChange={(e) => setUser(e.target.value.toLowerCase())}
        />
        <br />
        <button type='submit'>Enter</button>
      </form>
    </div>
  );
};

export default Home;
