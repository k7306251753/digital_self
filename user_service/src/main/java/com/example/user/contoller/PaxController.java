package com.example.user.contoller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import com.example.user.entity.Participant;
import com.example.user.service.PaxService;

import java.util.List;
import java.util.Optional;

@RestController
@RequestMapping("/empengagement")
@CrossOrigin(origins = "*")
public class PaxController {

    @Autowired
    private PaxService paxService;

    @GetMapping("/test")
    public String test() {
        return "OK";
    }

    @PostMapping("/createpax")
    public ResponseEntity<?> createPaticipant(@RequestBody Participant participant) {
        Participant newParticipant = paxService.save(participant);
        return new ResponseEntity<Participant>(newParticipant, HttpStatus.CREATED);
    }

    // Get all participants
    @GetMapping("/participants")
    public ResponseEntity<List<Participant>> getAllParticipants() {
        System.out.println("[PaxController] Fetching all participants...");
        List<Participant> participants = paxService.findAll();
        System.out.println("[PaxController] Found " + participants.size() + " participants.");
        return new ResponseEntity<>(participants, HttpStatus.OK);
    }

    // Get participant by ID
    @GetMapping("/participants/{id}")
    public ResponseEntity<Participant> getParticipantById(@PathVariable Long id) {
        Optional<Participant> participant = paxService.findById(id);
        return participant
                .map(value -> new ResponseEntity<>(value, HttpStatus.OK))
                .orElseGet(() -> new ResponseEntity<>(HttpStatus.NOT_FOUND));
    }

    // Update participant
    @PutMapping("/participants/{id}")
    public ResponseEntity<Participant> updateParticipant(@PathVariable Long id, @RequestBody Participant participant) {
        Optional<Participant> updated = paxService.update(id, participant);
        return updated
                .map(value -> new ResponseEntity<>(value, HttpStatus.OK))
                .orElseGet(() -> new ResponseEntity<>(HttpStatus.NOT_FOUND));
    }

    // Delete participant
    @DeleteMapping("/participants/{id}")
    public ResponseEntity<Void> deleteParticipant(@PathVariable Long id) {
        boolean deleted = paxService.delete(id);
        return deleted ? new ResponseEntity<>(HttpStatus.NO_CONTENT) : new ResponseEntity<>(HttpStatus.NOT_FOUND);
    }
}
