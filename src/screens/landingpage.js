import React from "react";
import styles from "../styles/landingpage.module.css";
import virusguy from "../assets/calm_among_virus.jpg";
import logo from "../assets/whitequarancation.png";
import arrow1 from "../assets/arrow1.png";
import {
    Link,
  } from "react-router-dom";

const LandingPage = (props) => {
    return (
        <div>
            <div className={styles.rectangle}>
                <img className={styles.logo} src={logo} alt="logo"/>  
                    <div className={styles.title}>
                    Just 14 days until you’re back to the life you love!
                    </div> 
                    <Link to="/signup">
                        <div className={styles.button}>
                            <div className={styles.subtitle}>
                                Start now!
                            </div>
                            <img className={styles.arrow} src={arrow1} alt="arrow"/>
                        </div>    

                    </Link>

            </div>
            <img className={styles.virusguy} src={virusguy} alt="virus guy"/>

        </div>
    );
};

export {LandingPage}