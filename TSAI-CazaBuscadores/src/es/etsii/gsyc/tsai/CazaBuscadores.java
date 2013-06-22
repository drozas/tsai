package es.etsii.gsyc.tsai;

import java.io.IOException;
import java.io.PrintWriter;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.Random;

public class CazaBuscadores {

	/**
	 * @param args
	 * 
	 * @author drozas
	 */
	public static void main(String[] args) 
	{
		// TODO Auto-generated method stub
		
		final String header = "HTTP/1.0 200 OK \r\nContent-Type: text/HTML \r\n\r\n" +
				"<html><head><meta content=\"text/html charset=ISO-8859-1\" http-equiv=\"content-type\">" +
				"<title>Cazabuscadores</title></head><body>";
		final String footer = "</body></html>";

		
		if(args.length==1)
		{

			int port = Integer.parseInt(args[0]);
			System.out.println("Running Cazabuscadores on port: " + port);
			
			ServerSocket srv = null;
			Socket cl = null;
			PrintWriter out = null;
		
			
			try
			{
				srv = new ServerSocket(port) ;

			}catch(IOException e)
			{
				System.out.println("Exception while creating ServerSocket! : " + e);
			}
			while(true)
			{
			    try 
			    {
	   
			    	cl = srv.accept();
			    	out = new PrintWriter(cl.getOutputStream());
	   
			    	//out.println("Hola")
			    	
			    	//Generate response
			    	out.print(header);
			    	Random rnd = new Random();
			    	int page = rnd.nextInt();
			    	out.print("<a href=\"" + page + ".html\">" + page  + "</a>");
			    	out.print(footer);
			    	out.close();
			    	cl.close();
	
	
			    }catch (IOException e) 
			    {
			           System.out.println("Exception on ClientSocket" + e);
			    }
			}
			

			
		}else{
			System.out.println("Use: Cazabuscadores <port>");
		}
			

	}

}
