import React, { Component } from "react";
import axios from "axios";
import { Container, Row, Col } from "reactstrap";

export default class AccountTable extends Component {
    constructor(props) {
        super(props)
        this.state = {
            account: this.props.activeAccount,
            currency: {},
        };
    }

    componentDidMount() {
        axios
            .get(`/api/accounts/${this.state.account.id}`)
            .then((res) => {
                this.setState({ account: res.data })
                axios
                    .get(`api/currencies/${res.data.currency}`)
                    .then((res) => this.setState({ currency: res.data }))
                    .catch((err) => console.log(err));
            })
            .catch((err) => console.log(err));
    }

    render() {
        return (
            <Container>
                <Row>
                    <Col><h1>{this.state.account.name}</h1></Col>
                    <Col align="right"><h1>{this.state.account.balance} {this.state.currency.symbol}</h1></Col>
                </Row>
                <Row>
                    <Col xs="3">Account type: {this.state.account.account_type}</Col>
                </Row>
            </Container>
        )
    }

}