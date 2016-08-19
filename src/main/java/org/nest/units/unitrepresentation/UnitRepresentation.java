package org.nest.units.unitrepresentation;

import java.util.Arrays;
import java.util.HashMap;
import java.util.Optional;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import com.google.common.base.Preconditions;

/**
 * @author ptraeder
 * Helper class. Controlled way of creating base representations of derived SI units.
 */

public class UnitRepresentation {
  private int magnitude;
  private int K,s,m,g,cd,mol,A;

  public void addMagnitude(int magnitude) {
    this.magnitude += magnitude;
  }

  public String serialize() {
    int[] result = { K, s, m, g, cd, mol, A, magnitude };
    return Arrays.toString(result);
  }

  public String prettyPrint(){
    String numerator =
        (K==1? "K * " : K>0? "(K**"+K+") * " :"")
        + (s==1? "s * " : s>0? "(s**"+s+") * " :"")
        + (m==1? "m * " : m>0? "(m**"+m+") * " :"")
        + (g==1? "g * " : g>0? "(g**"+g+") * " :"")
        + (cd==1? "cd * " : cd>0? "(cd**"+cd+") * " :"")
        + (mol==1? "mol * " : mol>0? "(mol**"+mol+") * " :"")
        + (A==1? "A * " : A>0? "(A**"+A+") * " :"");
    if(numerator.length() > 0 ){
      numerator = numerator.substring(0,numerator.length()-3);
      if(numerator.contains("*")){
        numerator = "("+numerator+")";
      }
    }else{
      numerator ="1";
    }
    String denominator =
        (K==-1? "K * " : K<0? "(K**"+-K+") * " :"")
        + (s==-1? "s * " : s<0? "(s**"+-s+") * " :"")
        + (m==-1? "m * " : m<0? "(m**"+-m+") * " :"")
        + (g==-1? "g * " : g<0? "(g**"+-g+") * " :"")
        + (cd==-1? "cd * " : cd<0? "(cd**"+-cd+") * " :"")
        + (mol==-1? "mol * " : mol<0? "(mol**"+-mol+") * " :"")
        + (A==-1? "A * " : A<0? "(A**"+-A+") * " :"");
    if(denominator.length()>1){
      denominator = denominator.substring(0,denominator.length()- 3);
      if(denominator.contains("*")){
        denominator = "("+denominator+")";
      }
    }else{
      denominator ="";
    }
    return (magnitude!=0? "e"+magnitude+"*":"")+ numerator + (denominator.length()>0? " / "+denominator : "");
  }

  static public Optional<UnitRepresentation> lookupName(String unit){
    for (String pre: SIData.getSIPrefixes()){
      if(pre.regionMatches(false,0,unit,0,pre.length())){
        //See if remaining unit name matches a valid SI Unit. Since some prefixes are not unique
        String remainder = unit.substring(pre.length());
        if(SIData.getBaseRepresentations().containsKey(remainder)){
          int magnitude = SIData.getPrefixMagnitudes().get(pre);
          UnitRepresentation result = new UnitRepresentation(SIData.getBaseRepresentations().get(remainder));
          result.addMagnitude(magnitude);
          return Optional.of(result);
        }
      }
    }if(unit.regionMatches(false,0,"e",0,1)) {//explicitly check for exponent
      UnitRepresentation result =  new UnitRepresentation(SIData.getBaseRepresentations().get("e"));
      try{
        Integer exponent = Integer.parseInt(unit.substring(1));
        result.addMagnitude(exponent);
        return Optional.of(result);
      }catch(NumberFormatException e){
        Preconditions.checkState(false,unit+ " is not recognized.");
      }
    }
    if(SIData.getBaseRepresentations().containsKey(unit)) { //No prefix present, see if whole name matches
      UnitRepresentation result = new UnitRepresentation(SIData.getBaseRepresentations().get(unit));
      return Optional.of(result);
    }
    try{
      UnitRepresentation unitRepresentation = new UnitRepresentation(unit);
      return Optional.of(unitRepresentation);
    }catch(Exception e){}
    //should never happen
    return Optional.empty();
  }

  public UnitRepresentation(int K, int s, int m, int g, int cd, int mol, int A, int magnitude) {
    this.K = K;
    this.s = s;
    this.m = m;
    this.g = g;
    this.cd = cd;
    this.mol = mol;
    this.A = A;
    this.magnitude = magnitude;
  }

  public UnitRepresentation(UnitRepresentation unit){
    this.K = unit.K;
    this.s = unit.s;
    this.m = unit.m;
    this.g = unit.g;
    this.cd = unit.cd;
    this.mol = unit.mol;
    this.A = unit.A;
    this.magnitude = unit.magnitude;
  }

  public UnitRepresentation(String serialized){
    Pattern parse = Pattern.compile("-?[0-9]+");
    Matcher matcher = parse.matcher(serialized);

    Preconditions.checkState(matcher.find());
    this.K = Integer.parseInt(matcher.group());
    Preconditions.checkState(matcher.find());
    this.s = Integer.parseInt(matcher.group());
    Preconditions.checkState(matcher.find());
    this.m = Integer.parseInt(matcher.group());
    Preconditions.checkState(matcher.find());
    this.g = Integer.parseInt(matcher.group());
    Preconditions.checkState(matcher.find());
    this.cd = Integer.parseInt(matcher.group());
    Preconditions.checkState(matcher.find());
    this.mol = Integer.parseInt(matcher.group());
    Preconditions.checkState(matcher.find());
    this.A = Integer.parseInt(matcher.group());
    Preconditions.checkState(matcher.find());
    this.magnitude = Integer.parseInt(matcher.group());
  }

  public UnitRepresentation divideBy(UnitRepresentation denominator){
    return new UnitRepresentation(
        this.K -denominator.K,
        this.s -denominator.s,
        this.m - denominator.m,
        this.g - denominator.g,
        this.cd - denominator.cd,
        this.mol -denominator.mol,
        this.A - denominator.A,
        this.magnitude - denominator.magnitude);
  }

  public UnitRepresentation pow(int exponent){
    return new UnitRepresentation(
        this.K * exponent,
        this.s * exponent,
        this.m * exponent,
        this.g * exponent,
        this.cd * exponent,
        this.mol * exponent,
        this.A * exponent,
        this.magnitude* exponent);
  }

  public UnitRepresentation multiplyBy(UnitRepresentation factor){
    return new UnitRepresentation(
        this.K +factor.K,
        this.s +factor.s,
        this.m + factor.m,
        this.g + factor.g,
        this.cd + factor.cd,
        this.mol +factor.mol,
        this.A + factor.A,
        this.magnitude + factor.magnitude);
  }

  public UnitRepresentation invert(){
    return new UnitRepresentation(-K,-s,-m,-g,-cd,-mol,-A,-magnitude);
  }
}