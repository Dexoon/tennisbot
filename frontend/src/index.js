import {createRoot} from 'react-dom/client';
import React from 'react';
import axios from "axios";
import {Container, Row, Col, Button} from "react-bootstrap";
import 'bootstrap/dist/css/bootstrap.min.css';

const texts = ['Финал', 'Полуфинал', 'Четвертьфинал', '1/8 финала', '1/16 финала', '1/32 финала', '1/64 финала', '1/128 финала', '1/256 финала']

const constructGrid = (predictions) => {
    let matchWinners = {};
    return matches.map((match) => {
        let newMatch = {round: match['round'], id: match['id']};
        if ('participant_one_id' in match) {
            newMatch['player_1'] = participants[match['participant_one_id']]
        } else {
            newMatch['player_1'] = matchWinners[match['preceding_match_one_id']]
        }
        if ('participant_two_id' in match) {
            newMatch['player_2'] = participants[match['participant_two_id']]
        } else {
            newMatch['player_2'] = matchWinners[match['preceding_match_two_id']]
        }
        if (predictions[match['id']] === true) {
            newMatch['winner'] = true
            matchWinners[match['id']] = newMatch['player_1']
        }
        if (predictions[match['id']] === false) {
            newMatch['winner'] = false
            matchWinners[match['id']] = newMatch['player_2']
        }
        return newMatch
    })

}

const Match = (({match: {round, id, player_1, player_2, winner}, setGrid, predictions}) => {
        const disabled = player_2 == null || player_1 == null || status === "og" || status === "fd"
        const [matchWinner, setMatchWinner] = React.useState(winner);
        const updatePredictions = (val) => {
            console.log(predictions)
            predictions[id] = val
            setGrid(constructGrid(predictions))
            axios.post('predictions/', predictions, {
                headers: {
                    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
                    'Content-Type': 'application/json;charset=utf-8',
                    "X-CSRFToken": csrftoken,
                },
            })
        }
        const setFirstWinner = () => {
            setMatchWinner(true);
            updatePredictions(true);
        }
        const setSecondWinner = () => {
            setMatchWinner(false);
            updatePredictions(false);
        }
        let [var_1, var_2] = ["info", "info"];
        if (matchWinner === true) {
            [var_1, var_2] = ["success", "secondary"]
        }
        if (matchWinner === false) {
            [var_1, var_2] = ["secondary", "success"]
        }
        return <Col fluid>
            <Row> <Button variant={var_1} onClick={setFirstWinner} style={{width: '400px'}}
                          disabled={disabled}>{player_1 || '---'}</Button></Row>
            <Row> <Button variant={var_2} onClick={setSecondWinner} style={{width: '400px'}}
                          disabled={disabled}>{player_2 || '---'} </Button></Row>
            <br/>
        </Col>
    }
)

const Round = ({roundMatches, round, setGrid, predictions}) => {
    return <div><Row>
        <h3>{texts[rounds - round - 1]}</h3>
        {roundMatches.map((match, idx) => <Match setGrid={setGrid} predictions={predictions} match={match} key={idx}/>)}
    </Row>
    </div>
}

const Board = ({grid, setGrid, predictions}) => {
    return <Container fluid style={{maxWidth: '1000%'}}>
        <Row>
            {Array.from(Array(rounds).keys()).map((round) => <Row key={100 + round}>
                <Round roundMatches={grid.filter((match) => match.round === round)} key={round}
                       setGrid={setGrid} predictions={predictions} round={round}/>
            </Row>)}
        </Row></Container>
}

const App = ({data: {id, name, predictions}}) => {
    const [grid, setGrid] = React.useState(constructGrid(predictions));
    return <div align={'center'}>
        <h1>{name}</h1>
        <Board grid={grid} setGrid={setGrid} predictions={predictions}/>
    </div>
};

export default App;

const container = document.getElementById('root');
const root = createRoot(container);
const matches = window.context['matches']
const rounds = window.context['round']
const status = window.context['status']
const participants = window.context['participants']
root.render(<App data={window.context}/>);