package com.example.user.serviceImpl;

import java.util.List;
import java.util.Optional;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.example.user.entity.Participant;
import com.example.user.reposetry.PaxReposetry;
import com.example.user.service.PaxService;

@Service
public class PaxServiceImpl implements PaxService {

	@Autowired
	private PaxReposetry paxReposetry;


	@Override
	public Participant save(Participant participant) {

		return paxReposetry.save(participant);
	}

	@Override
	public List<Participant> findAll() {
		return paxReposetry.findAll();
	}

	@Override
	public Optional<Participant> findById(Long id) {
		return paxReposetry.findById(id);
	}

	@Override
	public Optional<Participant> update(Long id, Participant participant) {
		return paxReposetry.findById(id).map(existing -> {
			// Update fields as needed
			existing.setUserName(participant.getUserName());
			existing.setPassword(participant.getPassword());
			// ...update other fields...
			return paxReposetry.save(existing);
		});
	}

	@Override
	public boolean delete(Long id) {
		if (paxReposetry.existsById(id)) {
			paxReposetry.deleteById(id);
			return true;
		}
		return false;
	}

}
