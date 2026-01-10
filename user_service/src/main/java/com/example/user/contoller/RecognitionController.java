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
        
        // Extract points, default to 100 if missing
        Long points = 100L;
        if (payload.containsKey("points") && payload.get("points") != null) {
            points = Long.valueOf(payload.get("points").toString());
        }

        String result = recognitionService.recognizeUser(senderId, receiverUsername, comment, points);
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
