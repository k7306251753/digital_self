package com.example.user.service;

import com.example.user.entity.Participant;
import com.example.user.entity.Address;
import com.example.user.entity.PhoneNumber;
import com.example.user.entity.Email;
import com.example.user.enums.Type;
import com.example.user.reposetry.PaxReposetry;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

import java.util.Collections;

@Component
public class DataInitializer implements CommandLineRunner {

    @Autowired
    private PaxReposetry paxReposetry;

    @Override
    public void run(String... args) throws Exception {
        if (paxReposetry.count() == 0) {
            System.out.println("Seeding local H2 database with dummy users...");

            Participant p1 = new Participant();
            p1.setUserName("krishna01");
            p1.setFullName("Neeli Krishna");
            p1.setDepartment("Engineering");
            p1.setUserType("Admin");
            p1.setPoints(2000L);
            p1.setBankAccountNumber(1234567890);
            p1.setPassword("securepass");

            Email e1 = new Email();
            e1.setEmail("A7306251753@gmail.com");
            e1.setType(Type.WORK);
            e1.setParticipant(p1);
            p1.getEmails().add(e1);
            paxReposetry.save(p1);

            Participant p2 = new Participant();
            p2.setUserName("john_doe");
            p2.setFullName("John Doe");
            p2.setDepartment("Sales");
            p2.setUserType("User");
            p2.setPoints(1000L);
            p2.setBankAccountNumber(9876543210L);
            p2.setPassword("paxpass");

            Email e2 = new Email();
            e2.setEmail("A7306251753@gmail.com"); // Using same for testing as requested
            e2.setType(Type.WORK);
            e2.setParticipant(p2);
            p2.getEmails().add(e2);
            paxReposetry.save(p2);

            Participant p3 = new Participant();
            p3.setUserName("alice_smith");
            p3.setFullName("Alice Smith");
            p3.setDepartment("Marketing");
            p3.setUserType("User");
            p3.setPoints(1000L);
            p3.setBankAccountNumber(1112223334L);
            p3.setPassword("alicepass");
            Email e3 = new Email();
            e3.setEmail("A7306251753@gmail.com");
            e3.setParticipant(p3);
            p3.getEmails().add(e3);
            paxReposetry.save(p3);

            Participant p4 = new Participant();
            p4.setUserName("bob_johnson");
            p4.setFullName("Bob Johnson");
            p4.setDepartment("HR");
            p4.setUserType("User");
            p4.setPoints(1000L);
            p4.setBankAccountNumber(5556667778L);
            p4.setPassword("bobpass");
            Email e4 = new Email();
            e4.setEmail("A7306251753@gmail.com");
            e4.setParticipant(p4);
            p4.getEmails().add(e4);
            paxReposetry.save(p4);

            System.out.println("PostgreSQL Seeding completed.");
        } else {
            System.out.println("Users already exist in database. Skipping seed.");
        }
    }
}
