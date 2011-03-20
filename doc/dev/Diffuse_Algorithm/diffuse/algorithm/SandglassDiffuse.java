package diffuse.algorithm;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Random;

import diffuse.Song;
import diffuse.SongAttribute;

/**
 * The Sandglass diffuse algorithm is based on the trickling of sand from
 * a Sandglass. It is similar to the Rigid Sandglass diffusion algorithm,
 * except that it is simpler and much more random based.
 * 
 * <p>Runtime: O(n) linear runtime.</p>
 * 
 * <p>Algorithm:</p>
 * <ol>
 * <li>Separate all of the songs by the song attribute grouping. This
 *     results in groups that we will name A, B, C, and so forth.</li>
 * <li>Find the biggest, divide its size by the sizes of all the others
 *     (including itself) and store this value with each group.</li>
 * <li>Start a counter. Every time the counter is incremented, add one to
 *     the value of each group counter. When a group counter goes over
 *     its limit, pop a random song out of the group and put it in a 
 *     global pool of songs, from which at the end one song is chosen.</li>
 * </ol>
 * 
 * @author Ben Morgan
 *
 */
public class SandglassDiffuse implements DiffuseAlgorithm {
	/**
	 * Move functions into a song group, which makes the
	 * entire algorithm implementation more understandble.
	 */
	private class SongGroup {
		private List<Song> localPool;
		private LinkedList<Song> songs;
		private double limit;
		private double counter;
		
		public SongGroup(List<Song> localPool) {
			this.localPool = localPool;
			songs = new LinkedList<Song>();
		}
		
		public void shuffle() {
			Collections.shuffle(songs);
		}
		
		public int size() {
			return songs.size();
		}
		
		public void setLimit(int base) {
			limit = (double)base / (double)songs.size();
		}
		
		public void addSong(Song s) {
			songs.add(s);
		}
		
		public void update() {
			if (size() > 0) {
				counter += 1;
				if (counter > limit) {
					localPool.add(songs.pop());
					counter -= limit;
				}
			}
		}
	}
	
	private Map<String, SongGroup> groups;
	private List<Song> localPool;
	private List<Song> finalOrder;
	private Random rand;

	@Override
	public List<Song> diffuse(List<Song> inputList, SongAttribute attr) {
		localPool = new LinkedList<Song>();
		finalOrder = new ArrayList<Song>(inputList.size());
		rand = new Random();
		init(inputList, attr);
		
		while (aggregatedSize() > 0) {
			update();
			// add all of the popped songs
			while(addRandomFromPool());
		}
		
		return finalOrder;
	}
	
	private boolean addRandomFromPool() {
		if (localPool.size() == 0)
			return false;
		int index = rand.nextInt(localPool.size());
		finalOrder.add(localPool.remove(index));
		return true;
	}
	
	private int aggregatedSize() {
		int size = 0;
		for (SongGroup sg : groups.values())
			size += sg.size();
		return size;
	}

	private void init(List<Song> inputList, SongAttribute attr) {
		if (inputList == null)
			throw new RuntimeException();
		
		groups = new HashMap<String, SongGroup>();
		for (Song s : inputList) {
			String sAttr = s.get(attr);
			SongGroup sGroup = groups.get(sAttr);
			if (sGroup == null) {
				sGroup = new SongGroup(localPool);
				groups.put(sAttr, sGroup);
			}
			sGroup.addSong(s);
		}
		
		// shuffle and find largest
		int max = 0;
		for (SongGroup sg : groups.values()) {
			sg.shuffle();
			if (sg.size() > max)
				max = sg.size();
		}
		
		// set the limits of the groups
		for (SongGroup sg : groups.values())
			sg.setLimit(max);
		
	}
	
	private void update() {
		for (SongGroup sg : groups.values())
			sg.update();
	}
}
