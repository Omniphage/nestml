package org.nest.nestml._visitor;

import de.monticore.literals.literals._ast.ASTIntLiteral;
import org.nest.nestml._ast.ASTExpr;
import org.nest.nestml._symboltable.typechecking.Either;
import org.nest.nestml._symboltable.symbols.TypeSymbol;
import org.nest.nestml._symboltable.unitrepresentation.UnitRepresentation;

import static de.se_rwth.commons.logging.Log.error;
import static org.nest.nestml._symboltable.typechecking.TypeChecker.*;
import static org.nest.nestml._symboltable.predefined.PredefinedTypes.*;

/**
 * @author ptraeder
 */
public class PowVisitor implements NESTMLVisitor {

  @Override
  public void visit(ASTExpr expr) {
    final Either<TypeSymbol, String> baseTypeE = expr.getBase().get().getType();
    final Either<TypeSymbol, String> exponentTypeE = expr.getExponent().get().getType();

    if (baseTypeE.isError()) {
      expr.setType(baseTypeE);
      return;
    }
    if (exponentTypeE.isError()) {
      expr.setType(exponentTypeE);
      return;
    }

    TypeSymbol baseType = baseTypeE.getValue();
    TypeSymbol exponentType = exponentTypeE.getValue();

    if (isNumeric(baseType) && isNumeric(exponentType)) {
      if (isInteger(baseType) && isInteger(exponentType)) {
        expr.setType(Either.value(getIntegerType()));
        return;
      }
      else if (isUnit(baseType)) {
        if (!isInteger(exponentType)) {
          final String errorMsg = CommonsErrorStrings.messageUnitBase(this, expr.get_SourcePositionStart());
          expr.setType(Either.error(errorMsg));
          error(errorMsg, expr.get_SourcePositionStart());
          return;
        }
        UnitRepresentation baseRep = UnitRepresentation.getBuilder().serialization(baseType.getName()).build();
        Either<Integer, String> numericValue = calculateNumericValue(expr.getExponent().get());//calculate exponent value if exponent composed of literals
        if (numericValue.isValue()) {
          expr.setType(Either.value(getTypeIfExists((baseRep.pow(numericValue.getValue())).serialize()).get()));
          return;
        }
        else {
          final String errorMsg = numericValue.getError();
          expr.setType(Either.error(errorMsg));
          error(errorMsg, expr.get_SourcePositionStart());
          return;
        }
      }
      else {
        expr.setType(Either.value(getRealType()));
        return;
      }
    }

    //Catch-all if no case has matched
    final String errorMsg = CommonsErrorStrings.messageType(
        this,
        baseType.prettyPrint(),
        exponentType.prettyPrint(),
        expr.get_SourcePositionStart());
    expr.setType(Either.error(errorMsg));
    error(errorMsg, expr.get_SourcePositionStart());
  }


  public Either<Integer, String> calculateNumericValue(ASTExpr expr) {
    //TODO write tests for this
    if (expr.isLeftParentheses()) {
      return calculateNumericValue(expr.getExpr().get());
    }
    else if (expr.getNumericLiteral().isPresent()) {
      if (expr.getNumericLiteral().get() instanceof ASTIntLiteral) {
        ASTIntLiteral literal = (ASTIntLiteral) expr.getNumericLiteral().get();
        return Either.value(literal.getValue());
      }
      else {
        return Either.error(CommonsErrorStrings.messageFloatingPointExponent(this, expr.get_SourcePositionStart()));
      }

    }
    else if (expr.isUnaryMinus()) {
      Either<Integer, String> term = calculateNumericValue(expr.getTerm().get());
      if (term.isError()) {
        return term;
      }
      return Either.value(-term.getValue());
    }

    return Either.error(CommonsErrorStrings.messageNonConstantExponent(this, expr.get_SourcePositionStart()));
  }

}

