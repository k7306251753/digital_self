package com.example.user.contoller;

import com.example.user.entity.Recognition;
import com.example.user.service.RecognitionService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/empengagement/recognize")
@CrossOrigin(origins = "*")
public class RecognitionController {

    @Autowired
    private RecognitionService recognitionService;

    @PostMapping
    public ResponseEntity<String> recognize(@RequestBody Map<String, Object> payload) {
        Long senderId = Long.valueOf(payload.get("senderId").toString());
        String receiverUsername = (String) payload.get("receiverUsername");
        String comment = (String) payload.get("comment");

        String result = recognitionService.recognizeUser(senderId, receiverUsername, comment);
        if (result.startsWith("Successfully")) {
            return ResponseEntity.ok(result);
        } else {
            return ResponseEntity.badRequest().body(result);
        }
    }

    @GetMapping("/received/{userId}")
    public ResponseEntity<List<Recognition>> getReceived(@PathVariable Long userId) {
        List<Recognition> recognitions = recognitionService.getReceivedRecognitions(userId);
        if (recognitions == null)
            return ResponseEntity.notFound().build();
        return ResponseEntity.ok(recognitions);
    }
}
