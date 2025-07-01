import React, { useState, useEffect } from 'react';
import './ViewAllResource.css';


const ViewAllResource = () => {

    const [data, setData] = useState([]);
    const [only_active, set_only_active] = useState(false);



    useEffect(() => {
        const fetchData = async () => {
            try {
                // const only_active = true;
                const response = await fetch(`http://localhost:8000/api/channel/get/all?only_active=${only_active}`);
                const responseData = await response.json();
                setData(responseData);
            } catch (error) {
                console.error('Error:', error);
            }
        };

        fetchData();
    }, [only_active]); // Empty dependency array to trigger the effect only once on component mount    


    const handleDelete = async (id) => {
        try {

            await fetch(`http://localhost:8000/api/channel/delete/${id}`, {
                method: 'DELETE'
            });
            // Reload the page after deletion
            window.location.reload();
        } catch (error) {
            console.error('Error deleting item:', error);
        }
    };

    const toggleHandler = () => {
        set_only_active(!only_active); // Toggle the value of isActive
    };



    return (
        <div className='container'>
            <h1> View All Allocated Resources </h1>

            <button type="button" style={{ marginRight: '15px' }} onClick={() => window.location.href = "allocateindex"} > Home </button>



            <br />
            <br />

            <div style={{ flexDirection: 'row' }}>
                <h3 style={{ marginRight: '35px' }}>Active Channels Only</h3>
                <div className={`toggle-container ${only_active ? 'active' : 'inactive'}`} style={{ marginLeft: '100px' }} onClick={toggleHandler}>
                    <div className="slider"></div>
                </div>
            </div>



            <br />
            <br />

            {data.length > 0 && (
                <table className="data-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Channel Active</th>
                            <th>Switch ID</th>
                            <th>Channel Number</th>
                            <th>Channel User</th>
                            <th>Action</th>
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
                                <td>
                                    <button style={{ background: 'red' }} onClick={() => handleDelete(item.id)}>Delete</button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}

        </div>
    );
}

export default ViewAllResource