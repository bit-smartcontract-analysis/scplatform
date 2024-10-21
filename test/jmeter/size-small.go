package main

import (
	"encoding/json"
	"fmt"

	"github.com/hyperledger/fabric-contract-api-go/contractapi"
)

type SmartContract struct {
	contractapi.Contract
}

// Auction data
type Voter struct {
	User         string             `json:"user"`
	Candidate    string             `json:"candidate"`
}

func (s *SmartContract) Set (ctx contractapi.TransactionContextInterface, user string, candidate string) error {

	//Validate

	voter := Voter {
		User: user,
		Candidate: candidate,
	}

	voterAsBytes, err := json.Marshal(voter)
	if err != nil {
		fmt.Printf("Marshal error: %s", err.Error())	
		return err
	}

	return ctx.GetStub().PutState(user, voterAsBytes)
}

func (s *SmartContract) Query (ctx contractapi.TransactionContextInterface, user string) (*Voter, error) {
	
	voterAsBytes, err := ctx.GetStub().GetState(user)
	if err != nil {
		fmt.Printf("Error obtaining data from user %s", err.Error())
		return nil, err
	}

	if voterAsBytes == nil {
		fmt.Printf("%s doesn't exist", user)
		return nil, err
	}

	voter := new (Voter)

	err = json.Unmarshal(voterAsBytes, voter)
	if err != nil {
		fmt.Printf("Unmarshal error %s", err.Error())
		return nil, err
	}

	return voter, nil
}