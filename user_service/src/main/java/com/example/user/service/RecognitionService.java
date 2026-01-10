package com.example.user.service;

import com.example.user.entity.Participant;
import com.example.user.entity.Recognition;
import com.example.user.reposetry.PaxReposetry;
import com.example.user.reposetry.RecognitionRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;

@Service
public class RecognitionService {

    @Autowired
    private PaxReposetry paxReposetry;

    @Autowired
    private RecognitionRepository recognitionRepository;

    @Autowired
    private EmailService emailService;

    @Transactional
    public String recognizeUser(Long senderId, String receiverUsername, String comment, Long points) {
        Participant sender = paxReposetry.findById(senderId).orElse(null);
        Participant receiver = paxReposetry.getByUserName(receiverUsername);

        if (sender == null)
            return "Sender not found.";
        if (receiver == null)
            return "Receiver not found.";
        if (sender.getPoints() < points)
            return "Not enough points.";

        // Transfer points
        sender.setPoints(sender.getPoints() - points);
        receiver.setPoints(receiver.getPoints() + points);

        paxReposetry.save(sender);
        paxReposetry.save(receiver);

        // Save recognition record
        Recognition recognition = new Recognition();
        recognition.setSender(sender);
        recognition.setReceiver(receiver);
        recognition.setPoints(points);
        recognition.setComment(comment);
        recognition.setTimestamp(LocalDateTime.now());
        recognitionRepository.save(recognition);

        // Send Email
        String emailTo = receiver.getEmails().isEmpty() ? "A7306251753@gmail.com"
                : receiver.getEmails().get(0).getEmail();
        String subject = "Congratulations, you have been recognized by " + sender.getFullName();
        String body = "Congratulations " + receiver.getFullName() + ",\n\n" +
                "You have been recognized in the DayMaker by " + sender.getFullName() + ".\n\n" +
                "Comment: " + comment + "\n\n" +
                "You earned " + points + " points!\n\n" +
                "Best regards,\n" +
                "The DayMaker Team";

        emailService.sendEmail(emailTo, subject, body);

        return "Successfully recognized " + receiver.getFullName();
    }

    public List<Recognition> getReceivedRecognitions(Long userId) {
        Participant user = paxReposetry.findById(userId).orElse(null);
        if (user == null)
            return null;
        return recognitionRepository.findByReceiver(user);
    }
}
