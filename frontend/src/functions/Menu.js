import React from 'react'
import styles from '../styles/Menu.module.css'

function Menu() {

  const handleButtonClick = (location) => {
    window.location.href = location;
  };

  return (
    <body className={styles.body}>
      <h1>Functions</h1>
      <div className={styles.button_container}>
        <button className={styles.button} onClick={() => handleButtonClick('/get-counter-data')}> Get Counter Data </button>
        <br />
        <button className={styles.button} onClick={() => handleButtonClick('/get-countrate-data')}> Get Count Rate Data </button>
        <br />
        <button className={styles.button} onClick={() => handleButtonClick('/get-counter-graph')}> Get Counter Graph </button>
        <br />
        <button className={styles.button} onClick={() => handleButtonClick('/get-photon-time')}> Photon Detection Time </button>
        <br />
        <button className={styles.button} onClick={() => handleButtonClick('/get-coincidence-count')}> Get Coincidence Count </button>
        <br />
        <button className={styles.button} onClick={() => handleButtonClick('/status')}> Status </button>
        <br />
      </div>
    </body>
  )

}

export default Menu