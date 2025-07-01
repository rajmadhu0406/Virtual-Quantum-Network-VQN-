import React, { useState } from 'react';
import './ViewUserResource.css';

const ViewUserResource = () => {

    const [username, setUsername] = useState('');
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (event) => {
        event.preventDefault();
        setLoading(true);

        try {
            const response = await fetch(`http://localhost:8000/api/channel/get/${username}`);
            const responseData = await response.json();
            setData(responseData);
        } catch (error) {
            console.error('Error:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className='container'>

            <h1> View Resources Allocated to User  </h1>

            <form onSubmit={handleSubmit}>
                <label>
                    Username:
                    <input
                        type="text"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                    />
                </label>
                <div style={{ flexDirection: 'row' }}>
                    <button type="submit" style={{ marginRight: '15px' }}>Submit</button>
                    <button type="button" style={{ marginRight: '15px' }} onClick={() => window.location.href = "allocateindex"} > Home </button>
                </div>
            </form>



            <br />
            <br />

            {loading && <div>Loading...</div>}

            <br />
            <br />


            {data.length > 0 && (
                <div className='table-container'>
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Channel Active</th>
                                <th>Switch ID</th>
                                <th>Channel Number</th>
                                <th>Channel User</th>
                            </tr>
                        </thead>
                        <tbody>
                            {data.map((item) => (
                                <tr key={item.id}>
                                    <td>{item.id}</td>
                                    <td>{item.channel_active.toString()}</td>
                                    <td>{item.switch_id}</td>
                                    <td>{item.channel_number}</td>
                                    <td>{item.channel_user}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}



        </div>
    );


};

export default ViewUserResource;
