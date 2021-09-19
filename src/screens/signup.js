import React from "react";
import styles from "../styles/signup.module.css";
import logo from "../assets/blackquarancation.png";

const SignUp = (props) => {
    return(
        <div>
            <div className={styles.heading}>
                <img className={styles.logo} src={logo} alt="logo"/>
                <h1>
                    Sign Up
                </h1>
            </div>
                
            <form className={styles.form}>
                <div>
                <label for="fname">Email:</label><br/>
                <input type="email" id="fname" name="fname" placeholder="Email address" /><br/>
                </div>
                <div>
                <label for="lname">Password:</label><br/>
                <input type="password" id="lname" name="lname"placeholder="Password" /><br/>
                </div>
                <div>
                <label for="fname">Full Name:</label><br/>
                <input type="text" id="fname" name="fname" placeholder="Name"/><br/>
                </div>
                <div>
                <label for="lname">Date of Birth:</label><br/>
                <input type="date" id="lname" name="lname" placeholder="DOB"/><br/>
                </div>
                <div>
                <label for="fname">Address:</label><br/>
                <input type="text" id="fname" name="fname" placeholder="Address Line"/><br/>
                </div>
                <div>
                    <label for="lname">City:</label><br/>
                    <input type="text" id="lname" name="lname" placeholder="City"/><br/>
                    </div>
                <div>
                    <label for="fname">Province:</label><br/>
                    <input type="text" id="fname" name="fname" placeholder="Province"/><br/>
                </div>
                <input type="file"/>
                <input type="submit"/>
                

            </form>


        </div>
    );
    

};

export {SignUp}