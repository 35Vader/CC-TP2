import java.io.File;
import java.io.FileNotFoundException;
import java.util.Scanner;

//Takes several lines from the file and splits them by spaces

//FILE:
//UM DOIS
//TRÊS QUATRO
//CINCO SEIS

//RETURNS:
//UM
//DOIS
//TRÊS
//QUATRO
//CINCO
//SEIS

public class Parser {

	public static void main(String[] args) {
		try {
			Scanner scanner = new Scanner(new File("./parser/myfile.txt"));
			while (scanner.hasNextLine()) {
				for (String s : scanner.nextLine().trim().split(" ")){
					System.out.println(s);
				};
			}
			scanner.close();
		} catch (FileNotFoundException e) {
			e.printStackTrace();
		}
	}

}
