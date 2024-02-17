import React, { Component } from "react";
import {
  Button,
  Modal,
  ModalHeader,
  ModalBody,
  ModalFooter,
  Form,
  FormGroup,
  Input,
  Label,
} from "reactstrap";
import axios from "axios";


export default class CustomModal extends Component {
  constructor(props) {
    super(props);
    this.state = {
      activeItem: this.props.activeItem,
      currencyList: [],
      userList: [],
      userDropdown: false,
      currencyDropdown: false,
    };
  }

  toggleUser = () => {
    this.setState({ modal: !this.state.userDropdown });
  }

  toggleCurrency = () => {
    this.setState({ modal: !this.state.currencyDropdown });
  }

  componentDidMount() {
    this.refreshLists();
  }

  refreshLists = () => {
    axios
        .get("/api/users/")
        .then((res) => this.setState({ userList: res.data }))
        .catch((err) => console.log(err));
    axios
        .get("/api/currencies/")
        .then((res) => this.setState({ currencyList: res.data }))
        .catch((err) => console.log(err));
  }

  handleChange = (e) => {
    let { name, value } = e.target;
    const activeItem = { ...this.state.activeItem, [name]: value || null};
    this.setState({ activeItem });
  };

  render() {
    const { toggle, onSave } = this.props;

    return (
      <Modal isOpen={true} toggle={toggle}>
        <ModalHeader toggle={toggle}>Account</ModalHeader>
        <ModalBody>
          <Form>
            <FormGroup>
              <Label for="account-owner">Owner</Label>
              <Input
                type="select"
                id="account-owner"
                name="user"
                value={this.state.activeItem.user || ''}
                onChange={this.handleChange}
                placeholder="Choose an account owner"
              >
                <option value=''></option>
                {this.state.userList.map(u => {
                    return (
                        <option value={u.id} selected={u.id === this.state.activeItem.user} >
                            {u.firstName} {u.lastName}
                        </option>
                    )
                })}
              </Input>
            </FormGroup>
            <FormGroup>
              <Label for="account-name">Name</Label>
              <Input
                type="text"
                id="account-name"
                name="name"
                value={this.state.activeItem.name}
                onChange={this.handleChange}
                placeholder="Enter an account name"
              />
            </FormGroup>
            <FormGroup>
              <Label for="account-currency">Currency</Label>
                <Input
                  type="select"
                  id="account-currency"
                  name="currency"
                  value={this.state.activeItem.currency || ''}
                  onChange={this.handleChange}
                  placeholder="Choose an account currency"
                >
                <option value=''></option>
                {this.state.currencyList.map(c => {
                    return (
                        <option value={c.identifier}>
                            {c.symbol}
                        </option>
                    )
                })}
                </Input>
            </FormGroup>
          </Form>
        </ModalBody>
        <ModalFooter>
          <Button
            color="success"
            onClick={() => onSave(this.state.activeItem)}
          >
            Save
          </Button>
        </ModalFooter>
      </Modal>
    );
  }
}