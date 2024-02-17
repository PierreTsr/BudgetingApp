import React, { Component } from "react";
import axios from "axios";
import { Table } from "reactstrap";

export default class AccountTable extends Component {
    constructor(props) {
        super(props)
        this.state = {
            account: this.props.activeAccount,
            currency: {},
            order: "-date",
            filter: {},
            transactions: [],
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
                this.refreshTransactions();
            })
            .catch((err) => console.log(err));
    }

    refreshTransactions = () => {
        axios
            .get(`api/transactions/?account=${this.state.account.id}${this.state.order ? '&ordering=' + this.state.order : ''}`)
            .then((res) => this.setState({ transactions: res.data }))
            .catch((err) => console.log(err));
    }

    sortBy = (col) => {
        switch(this.state.order) {
            case col:
                this.setState({ order: `-${col}`}, () => this.refreshTransactions());
                break;
            case `-${col}`:
                this.setState({ order: "" }, () => this.refreshTransactions());
                break;
            default:
                this.setState({ order: col }, () => this.refreshTransactions());
        }
    }

    renderItems = () => {
        return this.state.transactions.map((transaction) => (
            <tr>
            <th scope="row">
                {transaction.date}
            </th>
            <th>
                {transaction.payee}
            </th>
            <th>
                {transaction.value > 0 ? `${transaction.value} ${this.state.currency.symbol}`: "" }
            </th>
            <th>
                {transaction.value <= 0 ? `${-transaction.value} ${this.state.currency.symbol}`: "" }
            </th>
            </tr>
        ));
    }

    render() {
        return (
            <Table
                hover
                size=""
                striped
                >
                <thead>
                    <tr>
                    <th onClick={() => this.sortBy("date")}>
                        Date
                    </th>
                    <th onClick={() => this.sortBy("payee")}>
                        Payee
                    </th>
                    <th onClick={() => this.sortBy("value")}>
                        Credit
                    </th>
                    <th onClick={() => this.sortBy("value")}>
                        Debit
                    </th>
                    </tr>
                </thead>
                <tbody>
                    {this.renderItems()}
                </tbody>
                </Table>
        )
    }

}