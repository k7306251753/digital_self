package com.example.user.service;

import com.example.user.entity.Participant;

import java.util.List;
import java.util.Optional;

public interface PaxService {

    Participant save(Participant participant);

    List<Participant> findAll();

    Optional<Participant> findById(Long id);

    Optional<Participant> update(Long id, Participant participant);

    boolean delete(Long id);
}
