import React, { Component } from "react";
import AccountTable from "./components/AccountTable";
import AccountHeader from "./components/AccountHeader";
import axios from "axios";

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      viewCompleted: false,
      accountList: [],
      modal: false,
      activeItem: {
        name: "",
        owner: "",
        currency: "",
      },
    };
  }

  componentDidMount() {
    this.refreshList();
  }

  refreshList = () => {
    axios
      .get("/api/accounts/")
      .then((res) => this.setState({ accountList: res.data }))
      .catch((err) => console.log(err));
  };

  toggle = () => {
    this.setState({ modal: !this.state.modal });
  };

  handleSubmit = (item) => {
    this.toggle();

    if (item.id) {
      axios
        .put(`/api/accounts/${item.id}/`, item)
        .then((res) => this.refreshList());
      return;
    }
    axios
      .post("/api/accounts/", item)
      .then((res) => this.refreshList());
  };

  handleDelete = (item) => {
    axios
      .delete(`/api/accounts/${item.id}/`)
      .then((res) => this.refreshList());
  };

  createItem = () => {
    const item = { user: "", name: "", currency: "" };

    this.setState({ activeItem: item, modal: !this.state.modal });
  };

  editItem = (item) => {
    this.setState({ activeItem: item, modal: !this.state.modal });
  };

  renderItems = () => {
    const items = this.state.accountList

    return items.map((item) => (
      <li
        key={item.id}
        className="list-group-item d-flex justify-content-between align-items-center"
      >
        <span
          className='account-name mr-2'
          title={item.id}
        >
          {item.name}
        </span>
        <span
          className='account-currency mr-2'
          title={item.id}
        >
          {item.currency}
        </span>
        <span>
          <button
            className="btn btn-secondary mr-2"
            onClick={() => this.editItem(item)}
          >
            Edit
          </button>
          <button
            className="btn btn-danger"
            onClick={() => this.handleDelete(item)}
          >
            Delete
          </button>
        </span>
      </li>
    ));
  };

  render() {
    return (
      <main className="container">
        <AccountHeader activeAccount={{id:13}}/>
        <AccountTable activeAccount={{id:13}}/>
      </main>
    );
  }
}

export default App;