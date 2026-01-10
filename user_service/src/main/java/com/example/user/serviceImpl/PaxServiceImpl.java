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

	@Autowired
	private com.example.user.util.JwtUtils jwtUtils;

	@Override
	public Participant save(Participant participant) {
		return paxReposetry.save(participant);
	}

	@Override
	public List<Participant> findAll() {
		return paxReposetry.findAll();
	}

	@Override
	public Optional<Participant> findByUserName(String userName) {
		return Optional.ofNullable(paxReposetry.getByUserName(userName));
	}

	@Override
	public String authenticate(String username, String password) {
		Participant participant = paxReposetry.getByUserName(username);
		if (participant != null && participant.getPassword().equals(password)) {
			return jwtUtils.generateToken(username, participant.getUserId());
		}
		return null;
	}

	@Override
	public Optional<Participant> findById(Long id) {
		return paxReposetry.findById(id);
	}

	@Override
	public Optional<Participant> update(Long id, Participant participant) {
		return paxReposetry.findById(id).map(existing -> {
			existing.setUserName(participant.getUserName());
			existing.setFullName(participant.getFullName());
			existing.setPassword(participant.getPassword());
			existing.setDepartment(participant.getDepartment());
			existing.setUserType(participant.getUserType());
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
