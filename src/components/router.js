import React from "react";
import { Switch, Route, BrowserRouter } from 'react-router-dom';
import { LandingPage } from "../screens/landingpage";
import { SignUp } from "../screens/signup";

const Router = (props) => {
    return (
        <BrowserRouter>
        <Switch><Route exact path='/' component={LandingPage}/></Switch>
        <Switch><Route exact path='/signup' component={SignUp}/></Switch>
        </BrowserRouter>
    );
};

export {Router}