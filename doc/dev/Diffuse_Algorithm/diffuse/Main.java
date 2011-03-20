package diffuse;

import java.util.ArrayList;
import java.util.List;

import diffuse.algorithm.DiffuseAlgorithm;
import diffuse.algorithm.SandglassDiffuse;

public class Main {
	public static void main(String[] args) {
		int[] group1 = {55, 23, 31, 11, 26, 19};
		int[] group2 = {20, 10};
		int[] group3 = {33, 15, 15};
		
		List<Song> songs = generateSongs(group1, SongAttribute.ARTIST);
		
		DiffuseAlgorithm algo = new SandglassDiffuse();
		List<Song> playlist = algo.diffuse(songs, SongAttribute.ARTIST);
		
		printPlaylist(playlist, SongAttribute.ARTIST);
	}
	
	private static void printPlaylist(List<Song> playlist, SongAttribute attr) {
		String finalString = new String();
		String out = new String("_Start:");
		for (Song s : playlist) {
			if (out.startsWith(s.get(attr))) {
				out += s.get(attr);
			} else {
				System.out.println(out);
				finalString += " " + out;
				out = s.get(attr);
			}
		}
		System.out.println("\n\n" + finalString);
	}
	
	private static int sum(int[] array) {
		int sum = 0;
		for (int i : array)
			sum += i;
		return sum;
	}
	
	private static List<Song> generateSongs(int[] groups, SongAttribute attr) {
		List<Song> songs = new ArrayList<Song>(sum(groups));
		char attrName = 'A';
		
		for (int i : groups) {
			for (int j=0; j<i; j++) {
				Song s = new Song("","","");
				s.set(attr, Character.toString(attrName));
				songs.add(s);
			}
			attrName++;
		}
		
		return songs;
	}
}
